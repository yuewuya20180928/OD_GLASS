【ARS45 · demo 主板 · Waveshare 2.8" DSI 的 init 序列 + 背光电流 + RK3572 DSI 2-lane 支持】

## 背景 (老板 2026-11-04 01:18 拍板: demo 屏换成 Waveshare 2.8inch DSI LCD, SKU 22028)
· 屏侧 FPC **15 位 / 1.0mm**, MIPI DSI **2-lane** (DN0/DP0 + DN1/DP1 + CK), 官方逐针表已公开 (见
  `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` 的候选 ① 条目, 里面有完整 15 针表与 URL)
· ★**它的 init 序列在树莓派官方 firmware 里** (树莓派把它当 `waveshare,2.8inch-panel` 驱动) ⇒ 我们要把它
  **翻译成 Rockchip 的 `panel-init-sequence` 格式** (Rockchip 用 `panel-simple.c` + dts 里的寄存器写序列)

## 三件事 (★只写这 1 个文件, 不许碰别的)
`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md`

### ① init 序列: 树莓派 → Rockchip 格式
· 找到树莓派官方 firmware 里 **2.8inch-panel** 的 panel init (驱动在 `drivers/staging/panel/panel-waveshare-2p8inch.c` 一类)
· ★**逐条转成 Rockchip 格式**: Rockchip 的 `panel-init-sequence` 每条 = `<延迟us> 0x<reg> 0x<参数> 0x<参数> ...`
  (参照我们已有的 `HW/PCB/panel_simple_dsi_template.dtsi`, 那是 `rk3576-evb.dtsi` 里 263 条的格式)
· 给出**可直接粘贴**的 dts 片段 (面板节点: compatible / reg / width /height / dsi-format / dsi-lanes=2 /
  panel-init-sequence / panel-exit-sequence / orientation) ⇒ ★**并注明这是 2.8" 480×640 的参数**
· ★**同时给出 4-lane 版本的差异说明** (若屏是 2-lane, dsi-lanes 就是 2 ⇒ 我们主板只接 2 对差分)
· ★**证据等级**: init 序列必须指出**原始出处**(树莓派 firmware 的文件路径 + commit/版本) ⇒ 不许自己编

### ② 背光电流 (官方未公布 ⇒ 要靠证据)
· 屏的 15 针表里**没有背光脚** ⇒ 背光由模组内部从 3V3 取电 ⇒ ★**要知道这块屏从 3.3V 吃多少** (含背光)
· 查: 官方规格表的功耗/电流字段 / 同分辨率同面板的其他模组的电流 (做对比并标"推断")
· ⇒ 给出**我们 LIGHT_3V3 轨的电流预算修正值** (现在网表里标 150mA ⇒ 若屏要 300mA+, 我们那颗 TPS7A2033 就要换/并联)

### ③ RK3572 的 DSI 能不能只跑 2 lane + 支不支持 VESA DSC
· 查 Rockchip 内核 `dw_mipi_dsi` (rockchip-linux develop-6.12) 对 **DSI lane 数** 的支持 (1/2/4?)
  与 **DSC (VESA 显示流压缩)** 的支持 ⇒ ★给结论 + 代码路径/文档出处
· ★**为什么重要**: (a) 屏是 2-lane ⇒ 我们主板与 SoM 侧都可只做 2-lane ⇒ 省 4 个 SoM 脚 + 2 对差分走线
  (b) 整机目标 视崖 0.49" 的 datasheet 写明用 **VESA DSC 3:1** ⇒ ★**官方手册全文没提 DSC** ⇒ 若 SoM 侧不能解 DSC,
  那块屏就不能用 ⇒ ⇒ 这条必须查死

## 硬要求
- ★**只认原厂/官方资料** (树莓派官方 firmware / Rockchip 内核源码 / 厂商 datasheet); 第三方转述不许当证据
- ★**查不到写"未查到"** + 试过的 URL ⇒ **绝对不许编寄存器序列** (★编错 init = 屏烧了)
- init 序列**逐条照抄**, 不许"按经验改"

## 纪律
- ★**只写那 1 个文件**; 不许改 网表 / 板文件 / issue_log / tracker / STATE.yaml / 其它交付物
- 临时下载放 /tmp; 不发邮件 / 不联系厂家

## 汇报 (8~12 行)
init 序列转好了没有 (多少条) / 背光电流结论 / DSI 2-lane 结论 / DSC 结论 / 文件路径
