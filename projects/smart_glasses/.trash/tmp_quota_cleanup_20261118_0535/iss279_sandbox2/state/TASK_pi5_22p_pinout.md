【ARS45 · demo 主板 · 取 Raspberry Pi 5 的 22 位 MIPI DSI 座针位表 + 座型号/land pattern】

## 背景 (老板 2026-11-04 01:18 拍板: demo 屏换成 Waveshare 2.8")
· 屏 = **Waveshare 2.8inch DSI LCD (SKU 22028)**: 屏侧 FPC = **15 位 / 1.0mm**, MIPI DSI **2-lane**, 官方逐针表已公开:
  `1 GND / 2 DSI1_DN1 / 3 DSI1_DP1 / 4 GND / 5 DSI1_CN / 6 DSI1_CP / 7 GND / 8 DSI1_DN0 / 9 DSI1_DP0 / 10 GND / 11 SCL0 / 12 SDA0 / 13 GND / 14 3V3 / 15 3V3`
  (来源: https://docs.radxa.com 或 https://www.waveshare.com/wiki/2.8inch_DSI_LCD)
· Waveshare 原厂现成的线: **`DSI-Cable-12cm` = 15pin → 22pin** (给 Pi5 的 22 位 DSI1 座用)
⇒ ★**我们主板上要画的就是 Pi5 那个 22 位 / 0.5mm 的 DSI 座**, 直接吃这条现成的线 ⇒ **不自制转接线**

## 目标 (★只写这 2 个文件, 不许碰别的)
1. `HW/PCB/PI5_DSI_22P_PINOUT.md` —— **22 位座逐针表**: 脚号 | 信号名 | 说明 | 出处(URL + 页码/图号)
   + 头尾各一段: 座型号/厂商/间距/座型(翻盖 or 背夹)/板端还是屏端/出处
   + 结尾: "我们主板照这张表画座" 的说明 + 与 Waveshare 15→22 线的对应关系(哪一头接谁)
2. `HW/PCB/pi5_dsi_22p.json` —— `{"connector_model":"...","vendor":"...","pitch_mm":0.5,"positions":22,
   "source":"<URL>","pins":{"1":{"signal":"...","note":"...","source":"..."}, ... 22 项}}`

## 查找路径 (按优先级, 都要试并记录)
1. ★**Raspberry Pi 5 官方资料**: 官方 DSI 显示连接器的引脚定义 (Pi5 的 22 位 DSI 座) —— 树莓派官方文档/机械图
2. ★**Waveshare / Radxa 的 Pi5 扩展板与 DSI 排线资料** (他们的 15→22 线两端定义、Pi5 DSI 座型号)
3. ★**Pi5 载板原理图 / 机械图 PDF** (公开下载) ⇒ 座型号 + 针位表 + 机械尺寸
4. 公开 KiCad/立创 EDA 的 Pi5 DSI 座封装 (作为 land pattern 旁证, **不许当唯一出处**)
5. ★★**同时给出一条"我们自己画 footprint"的依据**: 座型号确定后, 找原厂 land pattern (HIROSE/其它厂商 PDF) 或 **官方 KiCad 库里的对应封装名 + 尺寸** ⇒ ★要能直接画 KiCad footprint

## 硬要求
- ★**只认原厂/官方资料** (树莓派官方 / Waveshare 官方 / Radxa 官方 / 座厂商原厂 PDF); 第三方转述不许当证据
- ★**查不到写"未查到"** + 列出试过的 URL + 失败原因 ⇒ **绝对不许猜针位**
- 22 个脚**都要有出处**; 若只有部分, 明确标哪几个是反推
- ★**顺带回答**: 我们板子上这个座是**翻盖式(front flip)还是背夹式(back flip)**? 屏模组的排线从**板上方还是下方**出线? (影响结构侧)
- ★**顺带确认**: 22 位里有没有"屏侧 15 位没有的脚"(例如额外的 GND/电源/或 DSI 的第 3/4 对差分) ⇒ 我们能不能用它们跑 4-lane

## 纪律
- ★**只写上面这 2 个文件**; 不许改 网表 / 板文件 / issue_log / tracker / STATE.yaml
- 临时下载放 /tmp; 不发邮件 / 不联系厂家 / 不下单

## 汇报 (8~12 行)
22 脚取到几项 / 座型号+座型 / pitch / 15→22 线的两端对应 / 我们能不能用那几脚跑 4-lane / 两个文件路径
