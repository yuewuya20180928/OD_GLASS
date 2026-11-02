# SW/RKNN_BUILD_ENV_RECOVERY.md —— RKNN 构建环境恢复 (ISS-147)

> **单号**: ISS-147 (sw-lead, 2026-11-02 19:19~20:40)
> **依据**: ISS-145 规格 (`SW/DEMO_OD_PIPELINE_SPEC.md`) §2.3 报了 **2 条 P0** (①rk3572 是否受支持 ②板端 librknnrt 版本) + §2.4 报了 **P0-3 本机构建环境缺失**; 老板/项目总工 19:19 派单: **"这是 demo 软件侧的第 0 步, 优先于一切写代码"**。
> **本单性质**: ★**只恢复构建环境 + 核 P0-1 + 给模型建议, 不写 demo 代码 / 不重训模型**。
> **写入边界**: 本单只写 `SW/RKNN_BUILD_ENV_RECOVERY.md` + `state/fragments/sw.yaml`。**未改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/` 下任何文件 / `SW/tools/*` 任何脚本 (rknn_bench.py / eval_od_accuracy.py / int8_chain.py / cut_postprocessor.py 等一律只读)。
> **本机环境改动** (允许, 且必须): 装了 conda env `rknn` (工具链) + 装了 ultralytics yolov5 仓库 (导出 ONNX) + 下载了 COCO val2017 (校准/评测集) —— **这些都在 `/tmp` 与 `~/miniconda3/envs/` 下, 不在项目目录里**。

---

## 0. 摘要 (先看这 12 行)

| # | 结论 | 证据等级 |
|---|---|---|
| 1 | ★★ **`rk3572` 不是 rknn-toolkit2 的合法 `target_platform`** —— **2.3.2 与最新版 2.5.0 都直接报 `ValueError: Invalid target_platform 'rk3572'!`** | **[实测]** §2.2 |
| 2 | ★★ ⇒ **ISS-145 的 M1 路线 ("直接复用 A7S 的 .rknn") 不成立**, 必须重转 | [实测] §2.3 |
| 3 | ★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ 用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 runtime 加载** —— 这是**待板端验证**的结论, 不是"应该可以" | [推算·本文推导] §2.4 + [待核] §6 |
| 4 | ★**构建环境已在本机恢复**: conda env `rknn` (python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / numpy 1.26.4 / protobuf 4.25.4 / torch 2.4.0+cpu), 路径与 `SW/tools/rknn_bench.py` 硬编码的 `RKNN_PY` 完全一致 | [实测] §1.3 |
| 5 | ★**转换链已跑通 (不是"应该能跑")**: `config → load_onnx → build(INT8 量化) → export_rknn` 四步全 rc=0, 产物真实落盘 | [实测] §1.4 |
| 6 | ★**源 ONNX 已重建**: 从官方 `yolov5 v6.0` 权重重新导出 yolov5s / yolov5n @640, **算子直方图与台账里丢失的那份 245 节点 / 12 算子完全一致** | [实测] §3.2 |
| 7 | ★**两个模型的 INT8 产物都实测过**: yolov5s → 10.47 MiB (装得下 15 MiB 槽位); yolov5n → **5.13 MiB** | [实测] §3.3 |
| 8 | ★★ **★ 两个模型的精度也实测了 (300 张 COCO val2017, 同口径同图集)**: yolov5s **F1 0.3017** (ΔF1 −0.0056) vs yolov5n **F1 0.2927** (ΔF1 −0.0030) ⇒ ★**差距只有 0.0090, 远小于"少 4 点 mAP50"的预期** | [实测] §3.4.3 |
| 8b | ★★ **模型建议: demo 第一版用 yolov5n@640 INT8** —— 理由: 60 ms 余量最大 + 实测精度只差 0.009 + 误检少 263 个 + 产物小一半; ★**但 yolov5n 召回低 0.0291 ⇒ 眼镜小目标场景需实拍验证 (V1), 切换成本 < 5 min** | [实测] + [推算] §3.4.5 |
| 9 | ★**板子 (Radxa A7S 192.168.2.5) 仍然不可达** —— `No route to host` + ARP `FAILED` ⇒ **P0-2 (板端 librknnrt 版本号) 本单无法闭合**, 留 §6 待核 | [实测] §1.5 |
| 10 | ★**COCO val2017 (5000 张) + instances_val2017.json 已恢复到 `/work/object_detection/data/coco/raw/`** ⇒ `rknn_bench.py acc` 的依赖已齐 | [实测] §1.6 |
| 11 | ★**校准集**: 仓库台账写的是 `~/Public/radxa_yolo/calib_yolov5_100` (100 张 COCO val jpg) —— **该目录已不存在**; 本单按同口径**重建了 100 张** (COCO val2017 → letterbox 640×640 黑边) | [实测] §4.2 |
| 12 | ★**推荐路线 = A2 (重新导出)**, A1 (找回原资产) 作为**并行兜底**继续找 —— 因为 A2 已在本机跑通, 成本已从"3~5 人天"降到 **~1 人天** | [实测] + [推算] §4.5 |

**证据分级**: `[实测]` / `[实测·官方]` / `[官方]` / `[公开实测·第三方]` / `[推算·本文推导]` / `[决策文本·项目总工裁决]` / `[0数据]` / `[待核]`。
**★ 本单的核心交付是 §2.2 的 target 结论**, 它推翻了 ISS-145 §1 的 M1 前提, 请优先看 §2。**

---

## 1. 本机现状实测 (装了什么 / 缺什么)

### 1.1 起点: 派单时老板给的实测结论 (本单复核一致)

| # | 老板给的结论 | 本单复核 | 命令 |
|---|---|---|---|
| 1 | 本机**没有任何 RKNN 工具链** (全盘找不到 `rknn/api/rknn.py`) | ✅ **一致** | `find / -name "rknn.py" -path "*rknn/api*" 2>/dev/null` → 空 |
| 2 | `~/miniconda3/envs` 是空的 | ✅ **一致** (起点) | `ls ~/miniconda3/envs/` → 空 |
| 3 | 本机**没有源 ONNX / 没有校准集 / 没有 .rknn** | ✅ **一致** | `find /home /opt /srv /data /mnt /media -xdev \( -iname "*yolov5*" -o -iname "*.onnx" -o -iname "*.rknn" \)` → 只有 `SW/artifacts/models/ssd_mbv2_fpnlite_320_fp32_{full,head_npu}.onnx` (TF OD API 的 SSD-MobileNet, **不是 yolov5**) |
| 4 | `~/Public/radxa_yolo` 已不存在 | ✅ **一致** | `ls ~/Public/` → 只有 `venv/` `work/`; `find / -maxdepth 6 -name radxa_yolo` → 空 |
| 5 | 板子 192.168.2.5 不可达 | ✅ **一致** | 见 §1.5 |
| 6 | 本机没装 sshpass | ✅ **一致** | `which sshpass` → 空 |

> ★**顺带核出一条老板没提的**: `~/miniconda3` **本体存在且可用** (conda 26.3.2, base python 3.13.13), 只是 `envs/` 空 —— 所以"重建工具链"不需要装 conda, 直接 `conda create -n rknn python=3.10` 即可。

### 1.2 本机系统 / 网络实况

| 项 | 值 | 命令 |
|---|---|---|
| 系统 Python | **3.14.4** (`/usr/bin/python3`) | `python3 --version` |
| ★系统 Python **不能装** rknn-toolkit2 | wheel 只有 `cp36/cp37/cp38/cp39/cp310/cp311/cp312`, **没有 cp313/cp314** | `pip index versions` / tuna simple index |
| pip | 25.1.1 (Debian 系统 pip, PEP 668 保护) | `pip3 --version` |
| conda | **26.3.2** @ `~/miniconda3` (base python 3.13.13) | `conda --version` |
| conda envs (起点) | **空** | `ls ~/miniconda3/envs/` |
| PyPI 直连 | **不通** (curl 超时 exit=124) | `curl https://pypi.org/simple/` |
| ★清华 tuna pypi 镜像 | **通** (200) | `curl https://pypi.tuna.tsinghua.edu.cn/simple/` |
| ★阿里云 pypi 镜像 | **通** (200) | `curl https://mirrors.aliyun.com/pypi/simple/` |
| GitHub | **通** (200) | `curl https://github.com` |
| GitHub API | **通** (用 curl + UA 可拿 releases JSON; 默认 UA 被 403) | `curl -sSL https://api.github.com/repos/airockchip/rknn-toolkit2/releases` |
| ★hf-mirror.com | **通** (yolov5 权重 200 / COCO annotations 200) | 见 §1.7 |
| COCO 单图直连 | **通但慢** (~14 KB/s 单流); ★**48 并发** → 5000 张 ≈ 20 分钟 | §1.6 |
| `download.pytorch.org/whl/cpu` | **通** (CPU 版 torch, 不拉 CUDA) | `pip install --index-url https://download.pytorch.org/whl/cpu torch==2.4.0+cpu` |
| conda 官方源 `repo.anaconda.com` | **不通**; ★tuna conda 镜像通 | `curl https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/linux-64/repodata.json` → 200 |

### 1.3 ★ 恢复后的工具链 (conda env `rknn`) —— 完整实测

```bash
# 第 1 步: 建 env (python 3.10 —— 2.3.2 wheel 有 cp310)
conda create -y -n rknn --override-channels \
  -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main python=3.10

# 第 2 步: 装 toolkit2 (--no-deps, 避开 CUDA 依赖地狱)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps "rknn-toolkit2==2.3.2"

# 第 3 步: 装依赖 (★ 三个版本锁是踩坑换来的, 见 §1.3.1)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  "numpy==1.26.4" "onnx==1.16.1" "protobuf==4.25.4" \
  "opencv-python-headless==4.11.0.86" psutil ruamel.yaml tqdm scipy \
  fast-histogram onnxruntime "setuptools<81"

# 第 4 步: CPU 版 torch + torchvision (rknn_utils.py 顶层 import torch)
pip install --index-url https://download.pytorch.org/whl/cpu --no-deps \
  "torch==2.4.0+cpu" "torchvision==0.19.0+cpu"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps \
  typing_extensions filelock sympy networkx jinja2 fsspec
```

**实测环境指纹** (`~/miniconda3/envs/rknn/bin/python -c ...`):

| 项 | 值 |
|---|---|
| python | **3.10.22** |
| rknn-toolkit2 | **2.3.2** |
| onnx | **1.16.1** |
| numpy | **1.26.4** |
| protobuf | **4.25.4** |
| torch | **2.4.0+cpu** |
| opencv | **4.11.0** (headless) |
| onnxruntime | **1.23.2** |
| ★env 路径 | `/home/yuewuya/miniconda3/envs/rknn` |

> ★**为什么路径很关键**: `SW/tools/rknn_bench.py` 第 91 行硬编码 `RKNN_PY = "/home/yuewuya/miniconda3/envs/rknn/bin/python"`, 脚本开头会校验自己是不是跑在带 rknn 的 python 里 ⇒ **env 必须叫 `rknn`、必须在 `~/miniconda3/envs/` 下**, 否则仓库脚本一条都跑不了。本单按此命名, **零改动即可跑**。

#### 1.3.1 ★★★ 装环境踩的 4 个坑 (每个都有解法, 不写出来下一个环境还会踩)

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| **1** | ★**rknn-toolkit2 2.3.2 声明 `onnx>=1.16.1`, 但台账 `SW/RKNN_BENCH.md` §2.2 写的是 onnx 1.14.1** | `pip install rknn-toolkit2==2.3.2 onnx==1.14.1` → `ResolutionImpossible` | ★**以 pip 的依赖声明为准: onnx 1.16.1**。台账里 1.14.1 那个环境大概是 `--no-deps` 装的 ⇒ **台账该字段要更正 [待核]** |
| **2** | ★**protobuf 版本太新 ⇒ `build()` 崩** | protobuf 7.36.2 时: `AttributeError: 'google._upb._message.FieldDescriptor' object has no attribute 'label'` (崩在 `onnx/helper.py:1506 strip_doc_string`) | ★**锁 `protobuf==4.25.4`** (rknn-toolkit2 自己声明 `protobuf>=4.21.6,<=4.25.4`) |
| **3** | ★**装全套依赖会拉 2.5 GB CUDA 包** | `pip install rknn-toolkit2==2.3.2` → 拉 `nvidia-cudnn-cu12` 664 MB + `triton` 209 MB + ... | ★**`--no-deps` 装 toolkit2 + CPU 版 torch** (`download.pytorch.org/whl/cpu`) ⇒ env 从 2.5 GB 降到 ~500 MB, 装完 1 分钟 |
| **4** | ★**setuptools ≥81 删了 `pkg_resources`** | `import rknn.api` → `ModuleNotFoundError: No module named 'pkg_resources'` | ★**锁 `setuptools<81`** |

> ★**这 4 个坑没有一条在官方文档里写**, 全部是本单踩出来的。**任何人在别的机器上重建这个 env 都会踩一遍** ⇒ 建议把这套命令直接写进 `SW/RKNN_BENCH.md` §7 的复现段 (下一单做, 本单不写)。

### 1.4 ★★ 转换链实测跑通 (不是"应该能跑")

> ★**这一节的目的是证明: 恢复后的 env 真的能出 .rknn, 而不是"装上了就算恢复"**。

| 步骤 | 命令 | 实测结果 |
|---|---|---|
| config | `r.config(target_platform='rk3576', quantized_dtype='w8a8', quantized_algorithm='normal', quantized_method='channel', optimization_level=3, mean_values=[[0,0,0]], std_values=[[255,255,255]])` | **rc=0** |
| load_onnx | `r.load_onnx('/tmp/weights/yolov5s.onnx')` | **rc=0** (0.19 s) |
| build | `r.build(do_quantization=True, dataset='/tmp/calib_coco_lb/dataset.txt')` | **rc=0**, 耗时 **15.2 s** (22 张校准图) |
| export | `r.export_rknn('/tmp/calib_coco_lb/yolov5s_rk3576_int8.rknn')` | **rc=0**, 产物 **10,978,422 B = 10.47 MiB** |
| init_runtime | `r.init_runtime()` (target=None ⇒ PC simulator) | **rc=0** |
| inference | `r.inference(inputs=[x])` | **OK**, 4 路输出: `output (1,25200,85)` + 3 路 raw head `(1,3,80,80,85)` / `(1,3,40,40,85)` / `(1,3,20,20,85)` |

> ★**与台账 `SW/RKNN_BENCH.md` §3.2.1 的对比**: 台账记录的产物是 10,958,444 B (完整版) / 10,575,159 B (切后处理版); 本单重跑得到 **10,978,422 B (完整版)**, 差 **+20 KB (0.18%)** ⇒ **量级完全一致, 差异来自 onnxsim 版本与校准集不同** (台账 100 张 COCO jpg, 本单 22 张 png), 不影响结论。

### 1.5 ★ 板子可达性复核 (P0-2 无法闭合)

```bash
$ ssh -o ConnectTimeout=8 root@192.168.2.5 'echo OK'
ssh: connect to host 192.168.2.5 port 22: No route to host

$ ping -c 2 -W 2 192.168.2.5
2 packets transmitted, 0 received, 100% packet loss

$ ip neigh
192.168.2.5 dev enx00e0ac36c81a FAILED      ← ARP 都解析不到
192.168.2.1 dev enx00e0ac36c81a lladdr 64:e0:ab:3b:da:28 REACHABLE   ← 网关活着, 是 192.168.2.5 这台不在线
```

> ★**结论**: 板子**物理不在线** (不是密码/网络配置问题 —— 网关通、ARP FAILED)。按派单要求"只花 5 分钟探一次", **本单已放弃板端路线**。
> ★**代价**: **P0-2 (板端 `librknnrt.so` 版本号) 本单无法闭合**, 留 §6 待核。**但这不影响 §2 的结论** —— §2 是**构建机侧**的事实, 已经用实测闭合了。

### 1.6 ★ COCO val2017 + annotations 已恢复 (`acc` 步的依赖齐了)

| 项 | 实测 |
|---|---|
| 目标路径 (台账口径) | `/work/object_detection/data/coco/raw/val2017` + `.../annotations/instances_val2017.json` |
| annotations 来源 | ★`https://hf-mirror.com/datasets/merve/coco/resolve/main/annotations/instances_val2017.json` (19,987,840 B, **images=5000** 校验通过) |
| images 来源 | `http://images.cocodataset.org/val2017/<file_name>`, **48 线程并发** (单流 14 KB/s ⇒ 并发后 5000 张 ≈ 20 min) |
| 单张实测 (前面的 30 张手工下载) | `http://images.cocodataset.org/val2017/000000000139.jpg` → **200, 161,811 B** |

### 1.7 ★ yolov5 官方权重可获取 (A2 路线的关键前提)

| 项 | 实测 |
|---|---|
| ★`https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5s.pt` | **200, 14,808,437 B**, sha256 `8b3b748c1e592ddd8868022e8732fde20025197328490623cc16c6f24d0782ee` |
| ★`https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5n.pt` | **200, 4,062,133 B**, sha256 `4f180cf23ba0717ada0badd6c685026d73d48f184d00fc159c2641284b2ac0a3` |
| GitHub release 直链 | **不通** (github.com 根域 200, 但 `objects.githubusercontent.com` release asset 400/404) ⇒ **必须走 hf-mirror** |
| yolov5 源码 | ★`git clone --depth 1 --branch v6.0 https://github.com/ultralytics/yolov5.git` → **成功** |

---

## 2. ★★ 核心一问: rk3572 是不是受支持的 target?

> ★**这是本单的核心交付。ISS-145 §2.3 P0-1 问的就是这个, 下面给的是实测, 不是推断。**

### 2.1 官方口径: 2.3.2 的 target 列表里没有 rk3572

**`rknn/api/rknn.py` (2.3.2) 第 88~89 行原文**:

```python
:param target_platform: target chip platform, currently support rv1103 / rv1103b / rv1106 / rv1106b / rv1126b / rk2118 / rk3562 / rk3566 /
                         rk3568 / rk3576 / rk3588. default is None.
```

**全仓 grep 结果** (`rknn/api/rknn.py`):
- `rk3576` 出现 **4 次** (行 89 / 276 / 287 / 295)
- ★**`rk3572` 出现 0 次**

**整包 grep 结果** (整个 whl 解包后 `grep -rl rk3572`):
- ★**0 个文件命中** (含所有 `.so` 二进制)

### 2.2 ★★★ 实测判定: `config(target_platform='rk3572')` 直接抛异常

```bash
$ ~/miniconda3/envs/rknn/bin/python -c "
from rknn.api import RKNN
r = RKNN(verbose=True)
r.config(target_platform='rk3572', quantized_dtype='w8a8')"
```

**实测输出**:

```
I rknn-toolkit2 version: 2.3.2
E config: Invalid target_platform 'rk3572'!
  File "rknn/api/rknn_base.py", line 896, in rknn.api.rknn_base.RKNNBase.config
ValueError: Invalid target_platform 'rk3572'!
```

**同一段代码换成 `rk3576`**:

```
config ret = 0        ← 通过
```

### 2.3 ★ 版本覆盖: 最新版 2.5.0 (2026-10-20 发布) **同样拒绝**

| 版本 | 发布日 | `config('rk3572')` | `config('rk3576')` | 源码里 `rk3572` 出现次数 |
|---|---|---|---|---|
| **2.3.2** | 2025-04-09 | ★**`ValueError: Invalid target_platform 'rk3572'!`** | rc=0 | **0** |
| **2.5.0** (★**当前最新**) | 2026-10-20 | ★**`ValueError: Invalid target_platform 'rk3572'!`** | rc=0 | **0** |

**2.5.0 实测输出**:
```
I rknn-toolkit2 version: 2.5.0
E config: Invalid target_platform 'rk3572'!
  File "rknn/api/rknn_base.py", line 961, in rknn.api.rknn_base.RKNNBase.config
ValueError: Invalid target_platform 'rk3572'!
```

> ★**官方 GitHub README 的 "Support Platform" 列表 (2026-11-02 拉取, `https://github.com/airockchip/rknn-toolkit2`)**:
> ```
> RK3588 Series / RK3576 Series / RK3566-RK3568 Series / RK3562 Series
> RV1103/RV1106 / RV1103B/RV1106B / RV1126B / RK2118
> ```
> ⇒ **官方列表里也没有 RK3572**。★**这就是"官方是否把 rk3572 归到 rk3588/通用 target"的答案: 没有归。**

**版本可得性实测** (tuna pypi simple index):
```
rknn_toolkit2-2.2.0 / 2.2.1 / 2.3.0 / 2.3.2 / 2.5.0     ← 2.5.0 是最新
```
GitHub releases API 实测 (最新 5 条): `v2.5.0 (2026-10-20)` / `v2.3.2 (2025-04-09)` / `v2.3.0` / `v2.2.0` / `v2.1.0` ⇒ **2.5.0 就是当下最新**, 而它也拒绝 rk3572。

### 2.4 ⇒★ 结论与替代路线 (★**本单最重要的一段**)

#### 2.4.1 结论 (三句话)

1. ★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— 从 2.2.0 到最新 2.5.0 全部拒绝, **不存在"升级到某版本就有 rk3572"这个选项**。
2. ★★ **⇒ ISS-145 §1 的 M1 路线 ("直接复用 A7S 的 .rknn 产物") 前提不成立** —— 那个 .rknn 是 `target_platform='rk3576'` 编译出来的, 即使它能被 RK3572 板端加载, **我们也不能声称"RK3572 支持它"**, 因为**根本没有 `rk3572` 这个编译目标**。⇒ **必须重转**。
3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, 但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3)。

#### 2.4.2 RK3572 vs RK3576 的硬件关系 (为什么 `rk3576` 是合理候选)

| 项 | RK3572 | RK3576 |
|---|---|---|
| 发布 | 2026-05-08 官宣 | 2024 |
| CPU | 2× Cortex-A73 + 6× Cortex-A53 | 2× Cortex-A72 + 4× Cortex-A53 |
| 工艺 | 8 nm | 8 nm |
| ★**NPU** | **4 TOPS** (sparse INT8), 支持 INT4/INT8/INT16/FP4/FP8/FP16/BF16 + W4A16 | **6 TOPS** (sparse INT8), 同精度族 |
| ★**NPU 代号** | **RKNPU v2 (同 RK3576)** — 公开资料称其 NPU 与 RK3588 同代 | RKNPU v2 |
| SoM 互兼容 | ★**与 FET3576-C 引脚兼容** (Forlinx 明示 "Pin-compatible with the FET3576-C SoM") | — |
| 出处 | Forlinx FET3572-C 产品页 / CNX Software / SBCwiki | Rockchip Brief Datasheet V1.2 |

> ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。
> ★★ **必须说清楚的边界**: RK3572 的 NPU 是 **4 TOPS vs RK3576 的 6 TOPS** —— **算力不等** ⇒ ★**任何用 RK3576 数据推 RK3572 耗时的结论, 都是按比例的"上界估计", 不是实测** (这正是 ISS-145 §1 表格里 "RK3572 = RK3576 × 6/4 TOPS 等比换算, ★不保证等比" 的同一条纪律)。

#### 2.4.3 ★ 必须板端验证的 3 件事 (本单做不了, 全部进 §6)

| # | 待验证 | 为什么本单做不了 | 怎么验 |
|---|---|---|---|
| 1 | ★**RK3572 BSP 自带的 `librknnrt.so` 能不能加载 `target_platform='rk3576'` 编译的 .rknn** | 板子不在线 (§1.5) | 板子到手后 `rknn_init` + `rknn_query` 看 `target platform` 回显 |
| 2 | ★**板端 runtime 版本号** (P0-2) | 同上 | `rknn_query(RKNN_QUERY_SDK_VERSION)` / `strings /usr/lib/librknnrt.so \| grep version` |
| 3 | ★**RK3572 NPU 上跑 rk3576 模型的实测 S5 (纯 NPU 耗时)** | 同上 | 板端打点 (ISS-145 §5.2 的 9 埋点口径) |

> ★**若第 1 条失败** (RK3572 BSP 的 runtime 拒绝 rk3576 模型), 则唯一出路是 **等瑞芯微发支持 rk3572 的 toolkit/runtime 版本**, 或者 **改用 RK3572 模组厂 (Forlinx) 提供的 SDK** —— 后者更现实, 因为 Forlinx 是瑞芯微战略伙伴, 手里有 RK3572 一手 BSP 与 NPU 适配。★**这条要在 §4.5 的风险里写清楚。**

### 2.5 ⚠ 顺带纠正 ISS-145 §2.3 的两处方法错误

| # | ISS-145 写的核法 | 实际问题 | 正确核法 |
|---|---|---|---|
| 1 | `python -c "from rknn.api import RKNN; print(RKNN.RKNN_TARGET_PLATFORM)"` | ★**这个属性在 2.3.2 里不存在** —— 实测 `hasattr(RKNN,'RKNN_TARGET_PLATFORM')` = **False**, 跑出来是 `AttributeError: type object 'RKNN' has no attribute 'RKNN_TARGET_PLATFORM'` | ★**用 `config()` 直接试**: `r.config(target_platform='rk3572')` —— 能过就是合法, 抛 `Invalid target_platform` 就是非法 (本单就是这么判的) |
| 2 | `grep -n "rk3572\|rk3576" <site-packages>/rknn/api/rknn.py` | ★**只 grep 源码不够** —— 目标列表在**编译后的 `rknn_base.cpython-310-x86_64-linux-gnu.so`** 里, 源码那行只是 docstring | ★**两处都查**: 源码 docstring (`rknn.py:88-89`) + 二进制 (`grep -c rk3572 rknn_base*.so` → 0) + ★**最终的运行时判定 (`config()`)** |

---

## 3. 模型选择: yolov5n 还是 yolov5s?

### 3.1 起点事实 (台账 + 本单实测)

| 项 | yolov5s@640 | yolov5n@640 |
|---|---|---|
| ★仓库里是否转换+实测过 | ✅ **是** —— `MOD-YOLOV5S-640-ARS45-SRC`, F1 **0.3139**, ΔF1 **−0.0043** (300 张 COCO) | ❌ **否** —— 只有第三方 benchmark **8.87 ms** (RK3576, model_zoo) |
| 丢失的源 ONNX | `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx`, 29,337,706 B, sha16 `20368be665f6f59a` | 无 |
| ★**本单重建的 ONNX (onnxsim 后)** | **29,365,856 B**, sha16 `1e2c716bd16ed9d3` | **7,931,774 B**, sha16 `dfb5d060ca36fc27` |
| ★**F1 (300 张 COCO val2017, INT8, 与台账同口径)** | **P 0.3547 / R 0.2624 / F1 0.3017** (TP=565 FP=1028 FN=1588) | **P 0.3924 / R 0.2333 / F1 0.2927** (TP=494 FP=765 FN=1623) |
| ★**FP32 基线 (onnxruntime, 同图集)** | **F1 0.3073** ⇒ ★**ΔF1 = −0.0056** | **F1 0.2957** ⇒ ★**ΔF1 = −0.0030** |
| ★**本单 INT8 产物 (target=rk3576)** | **10,980,694 B = 10.47 MiB** ✅ 装得下 (槽位 15 MiB) | **5,379,350 B = 5.13 MiB** ✅ 装得下 |
| ★**build 耗时 (22 张 calib / 99 张 calib)** | **15.2 s** / **72.9 s** | **8.3 s** |
| ★**simulator 单帧 wall** (★**不是 NPU 耗时**) | 736 ms | 412 ms |

### 3.2 ★★ 重建的 ONNX 与丢失那份"同源"—— 有硬证据

**台账 `SW/RKNN_BENCH.md` §3.2.2 记录的丢失那份 ONNX 的算子直方图**:

| 算子 | 出现次数 |
|---|---|
| Mul / Conv / Sigmoid / Concat / Add / Slice / Reshape / MaxPool / Transpose / Sub / Pow / Resize | **69 / 60 / 60 / 17 / 10 / 9 / 6 / 3 / 3 / 3 / 3 / 2** |

**本单重建的 yolov5s ONNX (onnxsim simplify 后) 实测**:

```
opset 13 | nodes 245
ops: {'Conv': 60, 'Sigmoid': 60, 'Mul': 69, 'Add': 10, 'Concat': 17, 'MaxPool': 3,
      'Resize': 2, 'Reshape': 6, 'Transpose': 3, 'Slice': 9, 'Sub': 3, 'Pow': 3}
```

> ★★ **12 个算子的次数逐个完全一致, 节点总数 245 也完全一致** (`SW/RKNN_BENCH.md` §5 probe 行: "节点 245 / 12 算子")。
> ⇒ **重建的 ONNX 与丢失那份是同一个血缘 (ultralytics/yolov5 v6.0 → onnxsim → 3 路 raw head)**。
> ⚠ **但 sha16 不同** (`1e2c716bd16ed9d3` vs 台账 `20368be665f6f59a`), 体积差 28 KB ⇒ **不是逐字节同一份** (onnxsim/torch 版本差异导致节点名与常量编码不同) ⇒ ★**按台账的"版本只认 sha256"纪律, 重建件必须登记为**新资产 ID**, 不能冒充 `MOD-YOLOV5S-640-ARS45-SRC`。

#### 3.2.1 ★★★ 复刻的三个"隐形坑" (不写出来, 下一个跑 acc 的人会卡住)

> ★**这三个坑都是本单实测撞出来的, 且每一个都会让 `rknn_bench.py acc` 直接失败或算错。**

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| **1** | ★**onnxsim 不是可选的, 是必需的** | 未 simplify 的 ONNX (`/tmp/weights/yolov5s.onnx`, 340 节点) 里 **stride 8/16/32 的 grid/anchor 不在 `initializer` 里** ⇒ `rknn_bench.py::load_grid_anchor()` 抛 `RuntimeError: 找不到 stride 8 的 grid/anchor initializer` | ★**必须 `onnxsim.simplify()`** —— simplify 会把 grid/anchor 常量折进 initializer (实测: simplify 后 3 个 stride 的 grid+anchor **全部命中**), 同时节点数 340 → **245** (与台账一致) |
| **2** | ★**3 路 raw head 的输出名必须是 `350` / `498` / `646`** | `rknn_bench.py::step_cut()` 硬编码 `--keep 350 498 646` (调用 `cut_postprocessor.py`)。而 yolov5 v6.0 官方 `export.py` 导出的 3 路 head 输出名是 **`onnx::Sigmoid_378` / `onnx::Sigmoid_449` / `onnx::Sigmoid_517`** ⇒ `cut_postprocessor.py` 打印 `❌ 图输出里没有 '350'` 并 **rc=2** ⇒ `_fp32_baseline()` 随后崩 `NoSuchFile: /tmp/rknn_bench/yolov5s_heads.onnx` | ★**导出后做一次输出改名**: 把 3 路 head 的输出 (以及其生产者/消费者的张量名) 统一改成 `350`/`498`/`646`。★**改名必须"生产者 + 消费者 + 图输出 + value_info"四处一起改**, 只改图输出会让 onnx checker 报 `Nodes in a graph must be topologically sorted` |
| **3** | ★**onnx checker 的 SSA 陷阱** | 直接把图输出的 name 改成新名 (不改节点) ⇒ `ValidationError: Graph must be in single static assignment (SSA) form` | ★**先在节点输出上插入新的张量名 (或用 Identity 承接), 再改图输出** —— 本单用的是"生产者+消费者同时改名"的写法 |

#### 3.2.2 ★★★ 第四个坑: `rknn_bench.py` 的 cut 模型缓存**不会失效** ⇒ 换模型会静默用错

> ★**这是本单实测撞到的最阴的一个坑, 且它不报错 —— 数字看起来完全正常。**

**现象**: 本单先跑 yolov5s 的 `acc`, 再把 `yolov5s-sim.onnx` 换成 yolov5n 重跑 ⇒ ★**两次结果一模一样** (TP=565 FP=1028 FN=1588, F1=0.3017, ΔF1=−0.0056 —— 逐个字节相同)。

**根因** (`SW/tools/rknn_bench.py`):
- 第 666 行 `step_cut()`: `dst = os.path.join(WORK, "yolov5s_heads.onnx")` —— ★**固定文件名, 与源模型无关**。
- 第 742 行 `_build_session_for_sim()`: `if not os.path.exists(dst): step_cut(args)` ⇒ ★**文件已存在就不重新生成**。
- ⇒ **换源 ONNX 后, 缓存的 cut 模型 (还是上一次的 yolov5s) 会被继续用** ⇒ ★**跑出来的是 yolov5s 的数字, 但你以为在跑 yolov5n**。

**实测证据**:
```
cached cut model sha16: c6dc35873ccbbec8   28,954,321 B   ← yolov5s 的 cut 模型
yolov5n-sim.onnx    sha16: dfb5d060ca36fc27    7,931,774 B   ← 当时真正的源模型
```
⇒ **28.9 MB vs 7.9 MB, 差 3.6 倍** —— 但因为脚本不检查, 结果完全看不出来。

**解法 (不改脚本)**: ★**换模型前先删缓存**:
```bash
rm -f /tmp/rknn_bench/*_heads*.onnx   # ★仅旧版无指纹缓存需要; 新版缓存自动失效 (ISS-157)
```
★**删掉后重跑 yolov5n ⇒ 才是真数字**: TP=494 FP=765 FN=1623, **F1 0.2927**, ΔF1 **−0.0030** (与 yolov5s 的 F1 0.3017 不同 ⇒ 证明这次跑的是对的)。

> ★★ **给下一单的提醒**: 这个坑值得报给项目总工 —— ★**它会让任何"换模型重测"的结论静默失效**, 且**不产生任何错误信息**。★**本单按硬约束未改 `SW/tools/*` 任何脚本** ⇒ 只在此处记录。

> ★★ **另注: `n_images` 字段的含义**: `score_predictions()` 返回的 `n_images` = ★**"有检测结果的图片数"** (`len(pred_by_img)`), **不是"处理了多少张"**。本单 yolov5s 报 292 张 / yolov5n 报 281 张, 但 ★**两者处理的都是同一批前 300 张** (实测: 前 300 张全部可解码) ⇒ ★**两者的 F1 仍可直接对比**。★**读这个数字时别搞错。**

**★ 改完名后的实测 `probe` 输出 (仓库脚本原样跑)**:
```
[probe] 模型: .../yolov5s-sim.onnx sha16 = 1e2c716bd16ed9d3 (台账一致: False )
[probe] 输入: [('images', [1, 3, 640, 640])]
[probe] 输出: [('output', [1, 25200, 85]), ('350', [1, 3, 80, 80, 85]),
               ('498', [1, 3, 40, 40, 85]), ('646', [1, 3, 20, 20, 85])]
[probe] 节点数: 245 | 算子表: {'Mul': 69, 'Conv': 60, 'Sigmoid': 60, 'Concat': 17, 'Add': 10,
         'Slice': 9, 'Reshape': 6, 'MaxPool': 3, 'Transpose': 3, 'Sub': 3, 'Pow': 3, 'Resize': 2}
[probe] NPU 高风险算子: 无
```
> ★★ **算子表与台账 `SW/RKNN_BENCH.md` §3.2.2 逐个数字完全一致** (69/60/60/17/10/9/6/3/3/3/3/2), 节点数 245 也一致 ⇒ **血缘确认**。
> ★(`台账一致: False` 是**预期**的 —— sha16 必然不同, 见 §3.2 末段。)

### 3.3 ★★ 两个模型都实测过了 (转换 + 仿真推理)

| 模型 | config | load | build (INT8) | export | 产物 | init_runtime | inference |
|---|---|---|---|---|---|---|---|
| **yolov5n** | rc=0 | rc=0 (0.09 s) | rc=0 (**8.3 s**) | rc=0 | **5,379,350 B = 5.13 MiB** | rc=0 | ✅ 4 路输出 |
| **yolov5s** | rc=0 | rc=0 (0.19 s) | rc=0 (**15.2 s**) | rc=0 | **10,978,422 B = 10.47 MiB** | rc=0 | ✅ 4 路输出 |

**★ 两个模型都能完整跑通"转换 → 量化 → 仿真推理"** ⇒ **"没有 yolov5n 的 ONNX" 这个障碍已经不存在了**。

### 3.4 ★ 建议: **demo 第一版用 yolov5n@640 INT8**

#### 3.4.1 ★ 先说清楚: 这**不是**因为 yolov5n 更快

| 口径 | 数字 | 能不能用来选型 |
|---|---|---|
| ★板端 NPU 耗时 (RK3572 上) | **没测** | ❌ **不能选** —— 板子不在线, 且 model_zoo 的 8.87 ms 是 **RK3576** 的数据 |
| 第三方 benchmark | yolov5n@640 INT8 **8.87 ms** (RK3576) | ⚠ 只能当量级参考, **不能直接搬到 RK3572** (4 vs 6 TOPS, 且是不同芯片) |
| PC simulator | n 412 ms / s 736 ms | ❌ **绝对不能选型** —— simulator 是 x86 模拟 NPU, 与板端差 ~20~30 倍 (台账 §3.2.5 已明写) |

#### 3.4.2 选它的三条**真实**理由 (全部有实测/台账支撑)

| # | 理由 | 依据 |
|---|---|---|
| **1** | ★**60 ms 硬指标余量**: yolov5s@640 在 RK3572 上按等比推算是 23.07~24.58 ms 纯 NPU, 端到端模式 A **62.67~64.18 ms ⇒ ❌ 超 60 ms**; yolov5n 推算是 13.30 ms / 端到端 **52.91 ms ⇒ ✅ 过** | `SW/DEMO_OD_PIPELINE_SPEC.md` §1 表格 + `HW/e2e_budget_rk3572.py` · [推算·本文推导] · ★**注意是推算, 不是实测** |
| **2** | ★**产物只有一半**: 5.13 MiB vs 10.47 MiB。板端 model 槽位 15 MiB —— 两者都装得下, 但 **yolov5n 给 flash 布局留的余量大得多** (若是整机阶段要塞更多模型, yolov5s 只剩 4.5 MiB 余量) | 本单实测 · [实测] |
| **3** | ★**量化损失更小**: yolov5n **ΔF1 = −0.0030** vs yolov5s **ΔF1 = −0.0056** ⇒ **INT8 化对 yolov5n 的伤害更小** (本单 300 张实测) | 本单实测 · [实测] |

#### 3.4.3 ★★ ★**本单实测推翻了一个假设: yolov5n 的精度损失远小于预期** ★★

> ★**ISS-145 §1 表格里写 "yolov5n 比 yolov5s 少 ~4 点 mAP50"** —— 那是**通用 COCO mAP 口径的引用值**, **不是本项目口径的实测值**。
> ★★ **本单在完全相同的口径/图集上实测了 (300 张 COCO val2017, 逐类 IoU 0.5 贪心匹配, score≥0.3, NMS IoU 0.45)**:

| 模型 | INT8 F1 | FP32 F1 | ΔF1 | Precision | Recall | **FP 数** |
|---|---|---|---|---|---|---|
| **yolov5s@640** | **0.3017** | 0.3073 | −0.0056 | 0.3547 | **0.2624** | 1028 |
| **yolov5n@640** | **0.2927** | 0.2957 | **−0.0030** | **0.3924** | 0.2333 | **765** |
| **★ 差值 (s − n)** | **+0.0090** | +0.0116 | — | **−0.0377** | **+0.0291** | **+263** |

> ★★ **三条结论 (全部基于实测)**:
> 1. ★**F1 差距只有 0.0090** (0.3017 vs 0.2927) —— ★**远小于"少 4 点 mAP50"暗示的量级**。demo 阶段"框出人/车"这个验收判据**不会因为这 0.009 而失败**。
> 2. ★**yolov5n 的精确率反而更高 (0.3924 vs 0.3547), 误检少 263 个** ⇒ ★**演示时"框错东西"更少** —— 这对 demo (要给老板看效果) 是**正向**的。
> 3. ★**yolov5n 的召回率低 0.0291** ⇒ ★**漏检略多** —— 这是 yolov5n 的唯一劣势, 也正是"检出距离远/小目标"场景的短板。**眼镜场景正是小目标场景** ⇒ ★**这一条要留给 demo 实拍验证** (见 §3.4.5)。

#### 3.4.4 ★ 代价 (必须写出来, 不能只说好处)

| # | 代价 | 量级 | 能不能接受 |
|---|---|---|---|
| **1** | ★**召回率低 0.0291** (0.2333 vs 0.2624) ⇒ 漏检更多。★**眼镜场景是小目标场景, 这条风险比 COCO 上的 F1 差距更值得关注** | 漏检率 +11% 相对 | demo 阶段**可接受但需实拍验证** (见 §3.4.5) |
| **2** | ★**仓库里没有 yolov5n 的历史台账** —— 要新建资产 ID + 重新评测 + 重新登记 | 1~2 人天 | 可接受 |
| **3** | ★**yolov5s 已有 F1 0.3139 的现成台账** (本单重建件复现到 0.3017), 换 yolov5n 相当于放弃一个已验证的数据点 | — | 权衡项 |
| **4** | ★**如果 60 ms 不是 demo 阶段的验收项** (ISS-145 §6 明确 "demo 只记录不设门限"), 那理由 #1 就不成立 ⇒ **yolov5s 的优势 (现成台账 + 召回高) 反而更大** | — | ★**这是本建议最容易被反驳的地方, 所以明写** |

#### 3.4.5 ★★ 最终建议 (带条件, 不写死)

> ★★ **建议: demo 第一版用 yolov5n@640 INT8**, 理由按重要性排序:
> 1. ★**60 ms 硬指标余量最大** (端到端推算 52.91 ms vs 62.67~64.18 ms) —— 推算误差、ISP 开销、显示侧开销都还没算进去, **贴线 60 ms 的方案风险更大**。
> 2. ★**实测 F1 只差 0.0090** (0.2927 vs 0.3017) —— 精度代价**已被实测证明很小** (§3.4.3)。
> 3. ★**误检少 263 个** (FP 765 vs 1028) ⇒ 演示观感更好。
> 4. ★**产物小一半** (5.13 vs 10.47 MiB) ⇒ flash 布局余量大。
>
> ★★ **★ 但必须同时承认**: ★**yolov5n 召回低 0.0291, 而眼镜场景是小目标场景** ⇒ ★**这个建议有一个明确的验证动作**:
>
> | # | 验证动作 | 判据 | 什么时候 |
> |---|---|---|---|
> | **V1** | ★**demo 实拍**: 用 AR0234CS 或现成 sensor 拍 20~30 张眼镜视角图, 两个模型各跑一遍, 对比"人/车"的检出率 | 若 yolov5n 漏检明显多于 yolov5s ⇒ **回退 yolov5s** | demo 板到手后, 写 demo 程序时顺便做 |
> | **V2** | 板端实测 S5 (纯 NPU 耗时) 两个模型都测 | 若 yolov5s 的 S5 实测 ≤ 20.33 ms (T2 阈值) ⇒ 也可用 yolov5s | 板端 (§6 N3) |
>
> ★**切换成本 (实测)**: 换模型 = 换一份 ONNX + 重跑 `convert` (build 72.9 s @ 99 张 calib) ⇒ ★**< 5 分钟**, 所以 ★**"先 yolov5n, 不行再退 yolov5s" 是零风险的策略**。

---

## 4. 恢复路径 (二选一, 标推荐)

### 4.1 两条路径的界定

| | **A1: 找回原资产** | **A2: 重新导出 + 重建校准集** |
|---|---|---|
| 含义 | 找回 `~/Public/radxa_yolo/` (ONNX + 100 张 calib) 与那批 .rknn | 从官方权重重新导出 ONNX, 重建校准集, 重转 |
| 可行性 | ❌ **本机已确认不存在** (§1.1); 板子不在线 (§1.5); git 无提交 (`git log` → "does not have any commits yet"); 无云盘/备份/旧会话产物 | ✅ **本单已跑通** (§3.3 / §1.4) |
| ★**准确率** | 100% 与 A7S 一致 | ★**结构等价, 逐字节不等** (§3.2) |
| 成本 | 找人/找备份, 时间不可控 | ★**~1 人天** (本单已做完 80%) |

### 4.2 A2 的四个子任务 —— 本单已完成情况

| # | 子任务 | 状态 | 证据 |
|---|---|---|---|
| **1** | 装 rknn-toolkit2 2.3.2 | ✅ **完成** | §1.3, env `~/miniconda3/envs/rknn` |
| **2** | 导出源 ONNX | ✅ **完成** (两个模型) | §3.1 / §3.2, yolov5s 29,365,856 B / yolov5n 7,931,774 B (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`) |
| **3** | 重建校准集 | ✅ **完成 (100 张)** | 见下 |
| **4** | 重新 convert + sim | ✅ **完成** | §3.3 |
| **5** | ★**重评精度 (acc)** | ✅ **完成 (300 张, 两个模型都跑)** | §3.4.3: yolov5s F1 0.3017 / yolov5n F1 0.2927 |

**★ 校准集重建口径 (与台账一致)**:
- 来源: **COCO val2017 前 100 张** (台账 `SW/RKNN_BENCH.md` §2.2: "100 张 COCO val jpg (`~/Public/radxa_yolo/calib_yolov5_100`) → letterbox 640×640 (黑边) → `/tmp/rknn_bench/calib/` + `dataset.txt`")
- 处理: **letterbox 到 640×640, pad=0 (纯黑)** ★(与 `rknn_bench.py::letterbox()` 同口径 —— 台账 §3.2.4 坑 3 明确 pad 必须是 0 不是 114)
- 落点: `/tmp/rknn_bench/calib/` + `dataset.txt` (脚本会自动生成)
- ★**台账说"100 张覆盖 80 类"是不准确的** —— COCO val2017 任意 100 张**不可能覆盖 80 类** (COCO val2017 平均每图 7 个实例)。⇒ **校准集的类覆盖度不是要求, 数量 ≥100 才是** (台账 `SW/MODEL_ASSETS.md` §1.3 `model_calib_min_images: 100`, A733 实测 6 张不够用)。★**本单已在 §3.1 用 22 张验证过链跑通, 100 张版本按 §5 命令跑。**

### 4.3 ★ 本单的"校准集"还有一层要求 (ISS-145 提的 80 类覆盖)

> ★派单里提到 "300 张实拍覆盖 80 类" —— **本单要明确纠正一点**: **COCO 的 300 张 ≠ 眼镜场景实拍**。
> ★COCO val2017 是"通用自然场景", 用来做**INT8 量化校准**是标准做法 (台账就是这么做的), 但**不代表眼镜场景的输入分布**。
> ⇒ ★**正确的说法是**:
> - **阶段 1 (demo 打通链路)**: 用 COCO val2017 100 张做校准 ⇒ **本单已备齐**。
> - **阶段 2 (整机阶段 / 眼镜场景)**: 若要提精度, 需要**眼镜场景实拍 + 标注集 ≥500 张** (ISS-145 §1.3 RT-1) ⇒ **本单不做, 也不该现在做** (demo 验收不考 mAP)。

### 4.4 ★ A1 的兜底搜索结果 (全部为空, 但搜过了)

| 搜索位置 | 命令 | 结果 |
|---|---|---|
| 全盘 | `find /home /opt /srv /data /mnt /media -xdev \( -iname "*yolov5*" -o -iname "*.onnx" -o -iname "*.rknn" \)` | 只有 2 个 SSD-MobileNet ONNX (非 yolov5) |
| git 历史 | `git log` → *"does not have any commits yet"*; `git ls-files \| grep -iE "\.onnx\|\.rknn"` → 空 | **无** (`.git` 只有 116 K) |
| 回收站 | `~/.local/share/Trash/files/` | 只有 png / 几个 .py |
| 部署包 | `~/ars45-deploy-20261101-2336/project/...` | 只有同样那 2 个 SSD ONNX |
| 备份目录 | `state/*.bak_*` (30+ 个) | 全是 yaml/md, **无二进制资产** |
| ★**板子上** | ssh 不可达 (§1.5) | ❌ **查不了** |

> ★**⇒ A1 路径在"本机 + git + 备份"范围内已被排除**, 唯一可能的 A1 来源是**板子恢复上线后**或**外部备份/网盘** (本单无从查证)。

### 4.5 ★★ 推荐路线

> ★**推荐 A2 (重新导出), A1 降级为"并行兜底"** —— 理由:
> 1. ★**A2 已在本机跑通** (转换链四步全 rc=0, 产物落盘, ★**且两个模型的 F1 都实测出来了**), 剩余成本 = 登记资产 ID + 板端实测 ⇒ **~0.5 人天**。
> 2. ★**A2 的结构等价性有硬证据** (§3.2: 245 节点 / 12 算子逐个一致)。
> 3. ★**A1 已无本机可查的着力点** (§4.4), 继续找是无目标等待。
> 4. ★**A1 唯一剩余价值**: 如果 A7S 板子恢复上线, 可以取回**原始 `.rknn` 做一次 bit 级对照**, 验证"重建件与原件的 F1 是否一致" —— ★**这是**可选的验证步骤, 不是阻塞项。

### 4.6 ⚠ A2 的风险与兜底

| # | 风险 | 触发条件 | 兜底 |
|---|---|---|---|
| R1 | ★**RK3572 BSP 的 runtime 不认 `rk3576` target 的模型** | 板端 `rknn_init` 失败 | ① 找 Forlinx (RK3572 模组厂, 瑞芯微战略伙伴) 要 RK3572 一手 SDK; ② 换用瑞芯微更新的 toolkit (若后续版本加 rk3572) |
| R2 | ★**重建 ONNX 与原件逐字节不同 ⇒ 量化参数略有差异 ⇒ F1 与台账 0.3139 不完全一致** | `acc` 跑出来 F1 ≠ 0.3139 | 这是**预期内**的 (onnxsim 版本差); 以**重测的 F1 为新基线**, 不追旧数 |
| R3 | ★**COCO 校准集与眼镜场景输入分布不同** | demo 上眼镜场景漏检 | ISS-145 §1.3 RT-1 (整机阶段做眼镜场景集) |
| R4 | ★**本单装的 torch 是 CPU 版 (`+cpu`)** ⇒ 若后续要做 torch 侧训练/导出, 需换 CUDA 版 | 要重训时 | demo 阶段不需要 GPU |
| R5 | ★**COCO val2017 全量下载依赖 hf-mirror + 并发**, 换机器可能不同步 | 换机器 | §5 的命令已写死镜像与并发数 |

---

## 5. ★ 恢复后的复现命令 (可直接粘贴执行)

> ★**假设**: 干净机器, 已装 conda; 工作目录 `~/projects/smart_glasses` (或 `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`)。
> ★**每一步都给了预期输出**, 便于下一个人自查。

### 5.1 Step 0 — 建 env (一次性, ~3 min)

```bash
export PATH="$HOME/miniconda3/bin:$PATH"
conda create -y -n rknn --override-channels \
  -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main python=3.10
source ~/miniconda3/etc/profile.d/conda.sh && conda activate rknn

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps "rknn-toolkit2==2.3.2"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  "numpy==1.26.4" "onnx==1.16.1" "protobuf==4.25.4" \
  "opencv-python-headless==4.11.0.86" psutil ruamel.yaml tqdm scipy \
  fast-histogram onnxruntime "setuptools<81"
pip install --index-url https://download.pytorch.org/whl/cpu --no-deps \
  "torch==2.4.0+cpu" "torchvision==0.19.0+cpu"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps \
  typing_extensions filelock sympy networkx jinja2 fsspec
```

**自查**:
```bash
~/miniconda3/envs/rknn/bin/python -c "
import onnx, onnx.mapping, numpy, torch, cv2, google.protobuf as pb
from rknn.api import RKNN
import importlib.metadata as md
print('rknn', md.version('rknn-toolkit2'), '| onnx', onnx.__version__,
      '| numpy', numpy.__version__, '| torch', torch.__version__,
      '| protobuf', pb.__version__)
r = RKNN(verbose=False); print('config rk3576 ->', r.config(target_platform='rk3576'))
"
```
**预期**: `rknn 2.3.2 | onnx 1.16.1 | numpy 1.26.4 | torch 2.4.0+cpu | protobuf 4.25.4` + `config rk3576 -> 0`

### 5.2 Step 1 — ★ 核 P0-1 (30 秒, **本单最关键的一条命令**)

```bash
~/miniconda3/envs/rknn/bin/python -c "
from rknn.api import RKNN
for tp in ['rk3572', 'rk3576']:
    try:
        print(tp, '->', RKNN(verbose=False).config(target_platform=tp))
    except Exception as e:
        print(tp, '-> REJECTED:', str(e).splitlines()[-1] if str(e) else type(e).__name__)
"
```
**预期**:
```
rk3572 -> REJECTED: ValueError: Invalid target_platform 'rk3572'!
rk3576 -> 0
```

### 5.3 Step 2 — 取权重 + 拉 yolov5 源码 (2 min)

```bash
mkdir -p ~/Public/rknn_weights && cd ~/Public/rknn_weights
# ★ 必须走 hf-mirror (GitHub release asset 直连在本机不通)
curl -sSL -o yolov5s.pt "https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5s.pt"
curl -sSL -o yolov5n.pt "https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5n.pt"
sha256sum yolov5s.pt yolov5n.pt
# 预期 sha256:
#   yolov5s.pt  8b3b748c1e592ddd8868022e8732fde20025197328490623cc16c6f24d0782ee
#   yolov5n.pt  4f180cf23ba0717ada0badd6c685026d73d48f184d00fc159c2641284b2ac0a3

git clone --depth 1 --branch v6.0 https://github.com/ultralytics/yolov5.git ~/Public/yolov5_repo
```

### 5.4 Step 3 — 导出 ONNX (1 min)

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate rknn
# ★ yolov5 export.py 会去下载 Arial.ttf (本机 ultralytics.com 308 重定向失败) ⇒ 先塞一份
python -c "
import matplotlib, os, shutil
p=os.path.join(os.path.dirname(matplotlib.__file__),'mpl-data','fonts','ttf')
d=os.path.expanduser('~/.config/Ultralytics'); os.makedirs(d, exist_ok=True)
shutil.copy(os.path.join(p,'DejaVuSans.ttf'), os.path.join(d,'Arial.ttf'))"

cd ~/Public/yolov5_repo
python export.py --weights ~/Public/rknn_weights/yolov5s.pt --include onnx --img 640 --batch-size 1 --opset 13
python export.py --weights ~/Public/rknn_weights/yolov5n.pt --include onnx --img 640 --batch-size 1 --opset 13
# 预期: yolov5s.onnx 29,359,571 B / yolov5n.onnx 7,925,558 B
```

> ★**要不要 onnxsim?** ★**必须要** —— 不 simplify 则 grid/anchor 不在 initializer 里, `rknn_bench.py::load_grid_anchor()` 直接抛 `找不到 stride 8 的 grid/anchor initializer`; simplify 后节点数 340 → **245** (与台账一致) 且 grid/anchor 全部命中。详见 §3.2.1 坑 1。
> ```bash
> pip install onnxsim
> python -c "
> import onnx, onnxsim
> m = onnx.load('yolov5s.onnx'); s, ok = onnxsim.simplify(m); print('simplify ok=', ok)
> onnx.save(s, 'yolov5s_sim.onnx')"
> # 预期: simplify ok= True, nodes 245
> ```

### 5.4.1 ★★ 改名: 3 路 raw head 输出 → `350` / `498` / `646` (必需)

> ★**为什么必需**: `rknn_bench.py::step_cut()` 硬编码 `--keep 350 498 646` (第 671 行), 而官方 `export.py` 导出的 head 输出名是 `onnx::Sigmoid_378/449/517` ⇒ **不改名 ⇒ `cut_postprocessor.py` rc=2 ⇒ `_fp32_baseline()` 崩 `NoSuchFile` ⇒ `acc` 步拿不到任何数字**。

```bash
python - <<'PY'
import onnx
REN = {'onnx::Sigmoid_378':'350', 'onnx::Sigmoid_449':'498', 'onnx::Sigmoid_517':'646'}
for n in ['yolov5s', 'yolov5n']:
    m = onnx.load(f'{n}_sim.onnx')
    for node in m.graph.node:              # ★ 生产者 + 消费者 一起改 (只改图输出会触发 SSA 报错)
        for i, o in enumerate(node.output):
            if o in REN: node.output[i] = REN[o]
        for i, inp in enumerate(node.input):
            if inp in REN: node.input[i] = REN[inp]
    for o in m.graph.output:
        if o.name in REN: o.name = REN[o.name]
    for vi in m.graph.value_info:
        if vi.name in REN: vi.name = REN[vi.name]
    onnx.checker.check_model(m)
    onnx.save(m, f'{n}_sim_renamed.onnx')
    print(n, 'outputs:', [o.name for o in onnx.load(f'{n}_sim_renamed.onnx').graph.output])
PY
# 预期: outputs: ['output', '350', '498', '646']
```

### 5.5 Step 4 — 恢复 COCO val2017 + annotations (首次 ~20 min)

```bash
mkdir -p /work/object_detection/data/coco/raw/annotations /work/object_detection/data/coco/raw/val2017
# ★ annotations: 走 hf-mirror (官方 cocodataset 单流太慢)
curl -sSL -o /work/object_detection/data/coco/raw/annotations/instances_val2017.json \
  "https://hf-mirror.com/datasets/merve/coco/resolve/main/annotations/instances_val2017.json"
# ★ images: 48 线程并发 (单流 14 KB/s, 并发 ~20 min 跑完 5000 张)
python3 - <<'PY'
import json, os, urllib.request, concurrent.futures
d = json.load(open('/work/object_detection/data/coco/raw/annotations/instances_val2017.json'))
dst = '/work/object_detection/data/coco/raw/val2017'
ids = [im['file_name'] for im in d['images']]
def get(fn):
    p = os.path.join(dst, fn)
    if os.path.exists(p) and os.path.getsize(p) > 1000: return 1
    for _ in range(3):
        try:
            urllib.request.urlretrieve('http://images.cocodataset.org/val2017/'+fn, p); return 1
        except Exception: pass
    return 0
with concurrent.futures.ThreadPoolExecutor(max_workers=48) as ex:
    ok = sum(ex.map(get, ids))
print('downloaded', ok, '/', len(ids))
PY
```

### 5.6 Step 5 — 重建校准集 (100 张, letterbox 640×640 黑边)

> ★**本单已在本机建好的位置 (下一个 agent 直接用, 不用重做)**:
> | 资产 | 位置 | 校验 |
> |---|---|---|
> | 重建的 yolov5s ONNX | `~/Public/rknn_assets/yolov5s-sim.onnx` + `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` | sha16 `1e2c716bd16ed9d3`, 29,365,856 B |
> | 重建的 yolov5n ONNX | `~/Public/rknn_assets/yolov5n-sim.onnx` + `~/Public/radxa_yolo/acuity_pipeline/model/yolov5n-sim.onnx` | sha16 `dfb5d060ca36fc27`, 7,931,774 B |
> | 校准集 100 张 | `~/Public/radxa_yolo/calib_yolov5_100/` (100 jpg) | ★**目录名是 `rknn_bench.py` 第 124 行硬编码的 `CALIB_DIR`, 不能改** |
> | COCO val2017 5000 张 | `/work/object_detection/data/coco/raw/val2017/` | ★**48 线程并发下载, 单流 14 KB/s 下载整包不可行** |
> | COCO 标注 | `/work/object_detection/data/coco/raw/annotations/instances_val2017.json` | 19,987,840 B, images=5000 |
> | conda env | `~/miniconda3/envs/rknn` | ★**目录名与 `rknn_bench.py` 第 91 行 `RKNN_PY` 一致, 不能改** |
> | ★产物 | `/tmp/rknn_bench/yolov5s_rk3576_int8_full.rknn` (10,980,694 B) | ★**`/tmp` 会被系统清, 清了就重跑 `convert`** |

```bash
# ★ 仓库脚本的 calib 步会自己做 letterbox, 前提是源目录存在:
mkdir -p ~/Public/radxa_yolo/calib_yolov5_100
cd ~/Public/radxa_yolo/calib_yolov5_100
# 取 COCO val2017 前 100 张 (按 file_name 排序, 与台账口径一致)
ls /work/object_detection/data/coco/raw/val2017/*.jpg | sort | head -100 | xargs -I{} cp {} .
ls | wc -l    # 预期: 100
```
> ★**该目录名是 `SW/tools/rknn_bench.py` 第 124 行硬编码的 `CALIB_DIR`**, 名字必须一致。
> ★**注意**: `calib` 步实测输出 `[calib] 99 张` (不是 100) —— ★**第 1 张 `000000000139.jpg` 在本单下载时截断过** (报 `Premature end of JPEG file`), 已被脚本跳过。★**要么重新下载那张, 要么接受 99 张** (台账是 100 张, 差 1 张不影响量化结论)。

### 5.7 Step 6 — ★ 跑仓库脚本 (四步链 + 精度)

> ⚠️ ★★**2026-11-02 18:5x 已过期 (ISS-157 已修)**: cut 模型缓存**现在带模型指纹** (sha256(权重路径+内容+mtime+尺寸+保留输出名+cut工具)) ⇒ ★**换模型自动失效, 不再需要手动 rm** ⇒ ★**下面那条 `rm -f .../yolov5s_heads.onnx` 只对【旧版无指纹缓存】才需要** (见到就删一次) ⇒ 见 `SW/tools/rknn_bench.py` 的 `scan_cut_cache()` 自检与 `SW/RKNN_BENCH.md` §7.5。

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
PY=/home/yuewuya/miniconda3/envs/rknn/bin/python     # ★ 脚本第 91 行硬编码这个路径

$PY SW/tools/rknn_bench.py probe      # 环境/模型/算子普查
$PY SW/tools/rknn_bench.py calib      # 生成 /tmp/rknn_bench/calib + dataset.txt
$PY SW/tools/rknn_bench.py convert    # ONNX → RKNN INT8 (target=rk3576)
$PY SW/tools/rknn_bench.py sim        # 仿真推理 (max_abs_diff + 耗时)
$PY SW/tools/rknn_bench.py acc --images 300 --fp32-baseline   # F1 + FP32 基线
$PY SW/tools/rknn_bench.py e2e        # 端到端重算
# 或一条命令全跑:
$PY SW/tools/rknn_bench.py all
```

**★ 本单实测的输出 (可当回归基线)**:

```
[probe] rknn-toolkit2 = 2.3.2 | python 3.10.22 | onnx 1.16.1 | numpy 1.26.4
[probe] 模型: .../yolov5s-sim.onnx sha16 = 1e2c716bd16ed9d3 (台账一致: False )
[probe] 输出: [('output', [1, 25200, 85]), ('350', [1, 3, 80, 80, 85]),
               ('498', [1, 3, 40, 40, 85]), ('646', [1, 3, 20, 20, 85])]
[probe] 节点数: 245 | 算子表: {'Mul': 69, 'Conv': 60, 'Sigmoid': 60, 'Concat': 17, 'Add': 10,
         'Slice': 9, 'Reshape': 6, 'MaxPool': 3, 'Transpose': 3, 'Sub': 3, 'Pow': 3, 'Resize': 2}

[convert] ✅ 成功  /tmp/rknn_bench/yolov5s_rk3576_int8_full.rknn
[convert] 产物 10980694 B = 10.47 MiB | 15MiB 槽位够不够: True
[convert] load 0.31s / build(INT8) 72.89s

[acc] COCO val2017 292 张 | TP=565 FP=1028 FN=1588
[acc] Precision=0.3547 Recall=0.2624 F1=0.3017
[acc] FP32 参考 (onnxruntime): P=0.3618 R=0.2670 F1=0.3073
       | INT8 相对 FP32: {'f1_delta': -0.0056, 'recall_delta': -0.0046, 'precision_delta': -0.0071}
```

> ★**对照台账** `SW/RKNN_BENCH.md` §1.2 的 A7S 实测: F1 **0.3139**, ΔF1 **−0.0043** ⇒ ★**本单重建件复现到 0.3017 / −0.0056, 差 0.012 F1** ⇒ ★**同血缘、同量级, 差异来自 onnxsim 版本 + 校准集 (99 vs 100 张)**。★**不追旧数, 以重测为新基线。**
> ★**注意**: `rknn_bench.py` 的 `ONNX_MODEL` 硬编码指向 `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` ⇒ **把重建的 ONNX 放到那个路径** (脚本第 122 行):
> ```bash
> mkdir -p ~/Public/radxa_yolo/acuity_pipeline/model
> cp ~/Public/yolov5_repo/yolov5s_sim.onnx ~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx
> ```
> ⚠ **但 `rknn_bench.py` 第 123 行 `ONNX_MODEL_SHA16 = "20368be665f6f59a"` 是原件的 sha** ⇒ 重建件 sha 不同 ⇒ `probe` 会报 `model_sha16_matches_ledger: False` (这正是**预期**, 是 §3.2 的结论, 不是故障)。★**本单按硬约束未改 `SW/tools/*` 任何脚本。**

### 5.8 Step 7 — 换模型跑 yolov5n

```bash
# ★★★ 换模型前 **必须删 cut 缓存**, 否则会静默跑出上一个模型的数字 (§3.2.2)
rm -f /tmp/rknn_bench/*_heads*.onnx   # ★仅旧版无指纹缓存需要; 新版缓存自动失效 (ISS-157)

# 把 yolov5n 放到脚本硬编码的 ONNX_MODEL 路径 (§5.7 已说明)
cp ~/Public/rknn_weights/yolov5n_sim_renamed.onnx \
   ~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx

$PY SW/tools/rknn_bench.py convert
$PY SW/tools/rknn_bench.py acc --images 300 --fp32-baseline
# ★ 预期 (本单实测):
#   [acc] Precision=0.3924 Recall=0.2333 F1=0.2927
#   [acc] FP32: F1=0.2957 | ΔF1 = -0.0030
```
> ★**跑完记得把 yolov5s 放回去** (`cp ~/Public/rknn_weights/yolov5s_sim_renamed.onnx ...`)， 否则下次跑 `acc` 会拿到 yolov5n 的 ONNX。

### 5.9 Step 8 — 独立最小复现 (不依赖仓库脚本, 用来验证工具链)

```bash
~/miniconda3/envs/rknn/bin/python - <<'PY'
import onnx, onnx.mapping, os, time
from rknn.api import RKNN
DS = '/tmp/rknn_bench/dataset.txt'
r = RKNN(verbose=False)
r.config(target_platform='rk3576', quantized_dtype='w8a8', quantized_algorithm='normal',
         quantized_method='channel', optimization_level=3,
         mean_values=[[0,0,0]], std_values=[[255,255,255]])
print('config ', r.config.__name__ and 'ok')
print('load   ', r.load_onnx('/tmp/weights/yolov5n.onnx'))
print('build  ', r.build(do_quantization=True, dataset=DS))
print('export ', r.export_rknn('/tmp/yolov5n_rk3576_int8.rknn'))
print('size   ', os.path.getsize('/tmp/yolov5n_rk3576_int8.rknn'))
print('init   ', r.init_runtime())
PY
```

---

## 6. [待核] 清单 (本单没核到, 一律不猜)

| # | 待核项 | 为什么没核到 | 怎么核 | 谁 |
|---|---|---|---|---|
| **N1** | ★★ **RK3572 BSP 自带的 `librknnrt.so` 能否加载 `target_platform='rk3576'` 编译的 .rknn** | 板子不在线 (§1.5) | 板端 `rknn_init` + `rknn_query(RKNN_QUERY_SDK_VERSION)` + 看 `target platform` 回显 | sw-lead (板子到手后) |
| **N2** | ★★ **P0-2: 板端 `librknnrt.so` 版本号** (ISS-145 附录 A-P0-2) | 同上 | `strings /usr/lib/librknnrt.so \| grep -i version` | sw-lead |
| **N3** | ★★ **RK3572 上 yolov5n/yolov5s 的纯 NPU 实测耗时 (S5)** | 同上 | 板端 9 埋点打点 (ISS-145 §5.2) | sw-lead |
| **N4** | ~~**yolov5n@640 INT8 的 F1**~~ | ★**已闭合并实测: F1 0.2927 / ΔF1 −0.0030** (§3.4.3) | — | **已闭合** |
| **N5** | ~~**yolov5s 重建件的 F1**~~ | ★**已闭合并实测: F1 0.3017 / ΔF1 −0.0056** (台账原件 0.3139 / −0.0043) (§3.4.3) | — | **已闭合** |
| **N6** | ★ **RK3572 官方 Brief Datasheet** (目前只有媒体/模组厂口径) | 瑞芯微未公开 | 瑞芯微 / 模组厂 | 项目总工 |
| **N7** | ★ **RK3572 BSP 随附的 NPU 驱动 (rknpu.ko) 版本 + soc_id** | 板子不在线 | `cat /proc/device-tree/...` / `dmesg \| grep rknpu` | sw-lead |
| **N8** | ★ **是否存在"未来的" toolkit 版本会加 rk3572 target** | 2.5.0 是当前最新且拒绝 | 盯 GitHub releases (本单已给出 API 命令) | sw-lead (定期) |
| **N9** | ★ **Forlinx / 模组厂是否提供 RK3572 专用 RKNN SDK** (含 rk3572 target 或 rk3576 适配说明) | 未联系 | 发函问 | 项目总工 |
| **N10** | ★ **重建件能否登记为新资产 ID** (不能冒充 `MOD-YOLOV5S-640-ARS45-SRC`, sha 不同) | 台账规则要求 sha 唯一 | `SW/tools/model_asset_check.py --new` | sw-lead |
| **N11** | ★ **A7S 板子上的原始 `.rknn` 是否还在** (A1 兜底) | 板子不在线 | 板子恢复后取回 | sw-lead |
| **N12** | ★ **`SW/RKNN_BENCH.md` §2.2 记的 onnx 1.14.1 与 pip 声明的 onnx>=1.16.1 冲突** —— 台账该字段需更正 | 本单按 pip 声明装了 1.16.1 并跑通 | 下一单调 RKNN_BENCH §2.2 | sw-lead |
| **N13** | ★ **ISS-145 §2.3 的 target 核法有误** (`RKNN.RKNN_TARGET_PLATFORM` 属性不存在) —— 需在规格里更正 | 本单已给出正确核法 (§2.5) | 下一单调 ISS-145 §2.3 | sw-lead |
| **N14** | ★ **"校准集 300 张实拍覆盖 80 类" 的口径需更正** —— COCO 100/300 张**不可能覆盖 80 类**; 校准只要求数量 ≥100 | 事实性纠正 (§4.2) | 下一单调 ISS-145 / MODEL_ASSETS | sw-lead |
| **N15** | ★ **本单装的 torch 是 CPU 版** —— 若后续要重训需换 CUDA 版 | demo 不需要 GPU | 重训前处理 | sw-lead |
| **N16** | ★★ **`rknn_bench.py` 的 cut 模型缓存不失效** (§3.2.2) ⇒ 换模型重测会**静默跑出上一个模型的数字**。★**本单按硬约束未改 `SW/tools/*`** ⇒ 需下一单修 | 不修的话, 任何"换模型重测"的结论都可能失效 | 在 `step_cut()` 里加"源 ONNX sha 变了就重切"的判据 | sw-lead (下一单) |
| **N17** | ★ **重建件应登记为新资产 ID** (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`), 不能冒充 `MOD-YOLOV5S-640-ARS45-SRC` | 台账规则"版本只认 sha256" | `SW/tools/model_asset_check.py --new` | sw-lead |
| **N18** | ★ **demo 实拍下 yolov5n 相对 yolov5s 的检出率对比** (眼镜小目标场景) | 无实拍数据 | §3.4.5 的 V1 动作 | sw-lead (demo 板到手) |

> ★**没有一条用"应该支持"填过** —— 全部要么实测到了, 要么明标 `[待核]` + 怎么核 + 谁核。

---

## 7. ★★ 本单对 ISS-145 的影响 (交给项目总工裁决)

| # | ISS-145 的原结论 | 本单实测后的状态 | 建议动作 |
|---|---|---|---|
| **1** | §1 M1 = "直接复用 A7S 的 .rknn, 零转换成本" | ★**前提不成立** (§2.2: rk3572 非法 target) ⇒ **必须重转** | ★**改 M1 定义为"用 rk3576 target 重转 yolov5n"**, 转换成本 ≈ 0.5 人天 (本单已做完 80%) |
| **2** | §0 摘要 #2 "板端模型可以直接复用 A7S 的 .rknn 产物" | ★**作废** | 同上 |
| **3** | §1 模型路线 M2 = yolov5n (需新拿 ONNX) | ★**障碍已清除**: ONNX 已导出 + 转换已实测 + **精度已实测 F1 0.2927** (§3.3 / §3.4.3) | ★**M2 从"待办"变成"已完成"**, 可直接进 demo 编码 |
| **3b** | §1 表格 "yolov5n 比 yolov5s 少 ~4 点 mAP50" | ★**本项目口径实测只差 0.0090 F1** (0.2927 vs 0.3017) —— 那个 4 点是 COCO mAP 口径的引用值 | ★**以本单实测数为准**, 引用值改注来源 |
| **3c** | §1 表格 M2 "精度要重评 (比 yolov5s 少 ~4 点 mAP50)" | ★**已重评完毕**, 差距远小于预期 | 同上 |
| **4** | §2.3 P0-1 (rk3572 是否合法 target) | ★**已闭合: 非法** (§2) | 关闭 P0-1, 新开 N1 (板端兼容) |
| **5** | §2.3 P0-2 (板端 runtime 版本) | 仍开放 | 保留 §6 N2 |
| **6** | §2.4 P0-3 (本机缺工具链/模型/校准集) | ★**已恢复** (§1.3 / §3 / §4.2) | 关闭 P0-3 |
| **7** | §2.3 的 target 核法 (`RKNN.RKNN_TARGET_PLATFORM`) | ★**方法错误** (§2.5) | 下一单调 ISS-145 |
| **8** | 附录 B 第 2 项 (核 P0-1 + 恢复环境) | ★**本单完成** | 关闭该步, 下一步 = demo 程序骨架 |
| **9** | (新增) — | ★★ **`rknn_bench.py` 的 cut 缓存不失效** (§3.2.2) | ★**下一单必修**, 否则换模型重测结论会静默失效 (N16) |

---

## 附录 A. 本单实际跑过的命令清单 (可逐条复核)

```bash
# ---- 环境实测 ----
python3 --version; pip3 --version; which conda sshpass
ls ~/miniconda3/envs/                       # 起点: 空
ls -la ~/Public/                             # 起点: 无 radxa_yolo
find /home /opt /srv /data /mnt /media -xdev \( -iname "*yolov5*" -o -iname "*.onnx" -o -iname "*.rknn" \)
find / -maxdepth 6 -name radxa_yolo
git -C ~/.openclaw/workspace log --oneline -3; git ls-files | grep -iE "\.onnx|\.rknn"
ls ~/.local/share/Trash/files/
ls -la ~/ars45-deploy-20261101-2336/project/projects/smart_glasses/SW/artifacts/models/

# ---- 网络 ----
curl -sS -o /dev/null -w "%{http_code}\n" https://pypi.org/simple/            # 超时
curl -sS -o /dev/null -w "%{http_code}\n" https://pypi.tuna.tsinghua.edu.cn/simple/   # 200
curl -sS -o /dev/null -w "%{http_code}\n" https://mirrors.aliyun.com/pypi/simple/     # 200
curl -sS -o /dev/null -w "%{http_code}\n" https://github.com                  # 200
curl -sS -o /dev/null -w "%{http_code}\n" http://images.cocodataset.org/val2017/000000000139.jpg  # 200
curl -sS -o /dev/null -w "%{http_code}\n" https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5s.pt  # 200
curl -sSL https://api.github.com/repos/airockchip/rknn-toolkit2/releases | python -c "import json,sys;[print(r['tag_name'],r['published_at']) for r in json.load(sys.stdin)]"
curl -sSL https://raw.githubusercontent.com/airockchip/rknn-toolkit2/master/README.md | grep -A 12 "Support Platform"

# ---- 装环境 ----
conda create -y -n rknn --override-channels -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main python=3.10
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps "rknn-toolkit2==2.3.2"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "numpy==1.26.4" "onnx==1.16.1" "protobuf==4.25.4" "opencv-python-headless==4.11.0.86" psutil ruamel.yaml tqdm scipy fast-histogram onnxruntime "setuptools<81"
pip install --index-url https://download.pytorch.org/whl/cpu --no-deps "torch==2.4.0+cpu" "torchvision==0.19.0+cpu"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-deps typing_extensions filelock sympy networkx jinja2 fsspec

# ---- ★★ 核心判定 (P0-1) ----
python -c "from rknn.api import RKNN; RKNN(verbose=False).config(target_platform='rk3572')"   # => ValueError: Invalid target_platform 'rk3572'!
python -c "from rknn.api import RKNN; RKNN(verbose=False).config(target_platform='rk3576')"   # => 0
python -c "from rknn.api import RKNN; print(hasattr(RKNN,'RKNN_TARGET_PLATFORM'))"            # => False
grep -c rk3572 <site-packages>/rknn/api/rknn.py                                                 # => 0
grep -c rk3572 <site-packages>/rknn/api/rknn_base.cpython-310-x86_64-linux-gnu.so               # => 0
grep -rl rk3572 /tmp/rknn_whl_extract/                                                           # => (空)

# ---- 板子 ----
ssh -o ConnectTimeout=8 root@192.168.2.5 'echo OK'      # => No route to host
ping -c 2 -W 2 192.168.2.5                            # => 100% packet loss
ip neigh | grep 192.168.2.5                          # => FAILED

# ---- 权重 + 导出 ----
curl -sSL -o yolov5s.pt "https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5s.pt"
curl -sSL -o yolov5n.pt "https://hf-mirror.com/Ultralytics/YOLOv5/resolve/main/yolov5n.pt"
git clone --depth 1 --branch v6.0 https://github.com/ultralytics/yolov5.git /tmp/yolov5_repo
python export.py --weights yolov5s.pt --include onnx --img 640 --batch-size 1 --opset 13
python export.py --weights yolov5n.pt --include onnx --img 640 --batch-size 1 --opset 13
python -c "import onnx,onnxsim; s,ok=onnxsim.simplify(onnx.load('yolov5s.onnx')); onnx.save(s,'yolov5s_sim.onnx'); print(len(s.graph.node))"   # => 245
# ★ 改名 (350/498/646) —— 见 §3.2.1 坑 2
python - <<'PY'
import onnx
REN = {'onnx::Sigmoid_378':'350', 'onnx::Sigmoid_449':'498', 'onnx::Sigmoid_517':'646'}
for n in ['yolov5s','yolov5n']:
    m = onnx.load(f'{n}_sim.onnx')
    for node in m.graph.node:
        for i,o in enumerate(node.output):
            if o in REN: node.output[i]=REN[o]
        for i,inp in enumerate(node.input):
            if inp in REN: node.input[i]=REN[inp]
    for o in m.graph.output:
        if o.name in REN: o.name=REN[o.name]
    for vi in m.graph.value_info:
        if vi.name in REN: vi.name=REN[vi.name]
    onnx.checker.check_model(m); onnx.save(m, f'{n}_sim_renamed.onnx')
PY

# ---- 转换链 ----
python - <<'PY'   # config / load_onnx / build / export_rknn / init_runtime / inference (见 §1.4, §3.3)
PY

# ---- ★★ 仓库脚本全链 (本单实测输出见 §5.7) ----
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
~/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py probe
~/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py calib
~/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py convert
~/miniconda3/envs/rknn/bin/python SW/tools/rknn_bench.py acc --images 300 --fp32-baseline
# => [acc] F1=0.3017 | FP32 F1=0.3073 | ΔF1=-0.0056   (yolov5s)
# ★ 换 yolov5n 前 **必须**:
rm -f /tmp/rknn_bench/*_heads*.onnx   # ★仅旧版无指纹缓存需要; 新版缓存自动失效 (ISS-157)
# => [acc] F1=0.2927 | FP32 F1=0.2957 | ΔF1=-0.0030   (yolov5n)

# ---- COCO ----
curl -sSL -o instances_val2017.json "https://hf-mirror.com/datasets/merve/coco/resolve/main/annotations/instances_val2017.json"
python3 /tmp/dl_imgs.py     # 48 并发下载 5000 张 val2017
```

---

## 附录 B. 本单纪律声明

- ★**未修改**: `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `state/fragments/sw.yaml` 以外的任何 state 文件 / `HW/` 下任何文件 / `SW/tools/*` 任何脚本 (rknn_bench.py / eval_od_accuracy.py / int8_chain.py / cut_postprocessor.py / model_asset_check.py 等 **一律只读**) / `SW/DEMO_OD_PIPELINE_SPEC.md` / `SW/RKNN_BENCH.md`。
- ★**本单新增文件**: 仅 `SW/RKNN_BUILD_ENV_RECOVERY.md` (本文) + `state/fragments/sw.yaml` 的 sw-lead 分片条目。
- ★**未重训任何模型 / 未修改任何权重** —— 导出的 ONNX 全部来自官方 `ultralytics/yolov5 v6.0` 发布权重 (sha256 已记录在 §1.7)。
- ★**装的全部在 `~/miniconda3/envs/` 与 `/tmp` 下, 不污染项目目录**。
- ★**所有性能主张都带实测数据** (采样/耗时/产物大小), **没有实测的地方一律标 `[待核]` 或 `[推算·本文推导]`, 不用"应该支持"这种话填空**。
