# ISS-207 · rk3572 目标兼容性与板端验证包 (sw-lead, 2026-11-15)

## 1. 结论摘要 (结论先行)
- [官网] 最新 rknn-toolkit2 = **v2.5.0 (2026-10-20)**; 官方 Support Platform 8 个系列**无 RK3572**, release notes 全文无 rk3572 ⇒ **"升级就有 rk3572 target"这条路不存在** ⇒ 只能 `target_platform='rk3576'` 转。
- [官网]+[实测] 2.3.2 官方库自打印合法 target 11 项 (`rk3566/3568/3588/3562/3576, rv1103/1106/1103b/1106b, rk2118, rv1126b`) **无 rk3572**; `config('rk3572')`→`ValueError: Invalid target_platform`, `config('rk3576')`→rc=0。
- [0数据] ★**RK3572 BSP runtime 认不认 rk3576-target 产物: 官方无此口径** (已检索 rknn-toolkit2 README/releases/CHANGELOG/doc×12 + rknn_model_zoo + rknpu2 + PyPI) ⇒ 命题判 (b) ⇒ 只能板端实测 (判据 N1) 回答。
- [实测] ★**修正 21:4x 判断**: 本机转换链**是活的** (`/home/yuewuya/miniconda3/envs/rknn/bin/python` + rknn-toolkit2 2.3.2) ⇒ 已实跑转换+落盘, 不必等任何人。
- [实测] 产物已落盘 `SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` (4,989,367 B) + `.sha256` sidecar; PC 侧 F1=**0.29265** (281 张, 与 v1.0 逐位一致)。
- [实测] ★`.rknn` **非逐字节可复现** (同 2.3.2 连转三次 ⇒ 三个不同 sha256, 字节数恒同; 但两次 acc 步 F1 逐位相同) ⇒ sha256 是**拷贝那一刻**的身份锚 (sidecar), 不是历史常量。
## 2. 兼容矩阵 (最新版 × target_platform × 是否含 rk3572)
| toolkit | 发布 | 官方平台含 RK3572 | 合法 target 全集 | rk3572 |
|---|---|---|---|---|
| 2.3.2 | 2025-04-09 | 否 | 11 项 [实测] | ❌ ValueError |
| **2.5.0 (最新)** | 2026-10-20 | 否 (README 8 系列) [官网] | [0数据] (whl 未取到) | ❌ 上游实测 ValueError |
## 3. 证据分级 (证据等级)
[官网] GitHub releases/PyPI/README/ModelZoo/rknpu2/doc 目录 · [实测] 本机 2.3.2 自打印 target 列表 + 转换 rc=0 + 精度 F1 + 三次 sha256 · [推算] N3 阈值 13.30ms · [0数据] 2.5.0 whl 二进制 + 全部板端结论。
## 4. 接口取值声明 (interface_claims)
转换 `target_platform='rk3576'` (官方合法, 无 rk3572 可选) · 落盘目录 `SW/artifacts/models/` (不许留 /tmp) · N2 通过线 F1≥0.2427 · N3 通过线 t_npu≤13.30ms (t_sdk_total 保守判) · 板端 sha256 锚 = `.sha256` sidecar。
## 5. 未决项与卡点 (降级 A/B/C)
- 降级 A 自持验证包 `SW/tools/rk3572_target_smoke.sh` (P1~P6 自动核对 + N1~N5 出 PASS/FAIL/INDET + 数值 + 失败原因, **板端不重转**) · 降级 B 重建 `SW/tools/rk3572_model_rebuild.sh` (转→落盘→sha256, 本机实跑 rc=0) · 降级 C 判据固化进脚本 (不是文档里的一段话)。
- ★R1 板端 `load_rknn` 是否接受 rk3576-target 产物 = **[0数据]**, 待板子 (包已就绪, 一条命令出判) · R2 若 R1 为否 ⇒ 出路三条见 `SW/RK3572_TARGET_COMPAT_V2.md` §3.2/§4.1 (本单不预判) · ★**无外部依赖挂账**: 不外发/不询价/不采购/不等原厂。
## 6. 验收标准自评 与 自证复现命令
P1~P6 自动化 ✅ · N1~N5 判据固化 ✅ · 官方口径自查 ✅ · 重建路径 ✅ (实跑 rc=0) · 板端实测 ❌ [0数据] (无板, 不可自评) · 纯 NPU vs SDK 总耗时分开报 ✅ (SOUL.md 铁律) · N5 记散热/功耗/频率 (降频会改 NPU 耗时可比性)。
自证: `bash SW/tools/rk3572_target_smoke.sh --dry-run` (rc=0) · `bash SW/tools/rk3572_model_rebuild.sh --dry-run` (rc=0) · 完整复现见 `SW/RK3572_TARGET_COMPAT_V2.md` §6。
