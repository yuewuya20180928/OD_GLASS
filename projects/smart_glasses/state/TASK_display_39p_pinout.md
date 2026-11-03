【ARS45 · demo 主板 · 取 Radxa Display 8HD 主板侧 39p/0.3mm 针位表 (blocker)】

## 背景 (为什么是 blocker)
我们用 **Radxa Display 8HD** 屏模组。其官方产品页 FPC 规格原文:
  "FPC Cable Specification: **39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)**"
  (另一版: "15-pin 1.0mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)")
⇒ ★★**我们主板上要画的是 39p/0.3mm 的座, 不是 40p/0.5mm** ⇒ 我们之前按 40p 画 ⇒ 与原厂排线对不上
⇒ ★★**更要命**: 项目里那张"40 针针位表"是**屏侧**的, 与**主板侧 39 针不是 1:1** ⇒
  ★**我们网表里 CONN_LIGHT 的针位编号现在是错的** (照的是屏侧 40 针) ⇒ 必须换成主板侧针位表。

## 交付物 (★只写这 2 个文件, 不许碰别的)
1. `projects/smart_glasses/HW/PCB/DISPLAY_39P_PINOUT.md`
   - **39 行针位表**: 脚号 | 信号名 | 说明 | 出处(URL + 页码/图号)
   - 开头: 连接器型号 / 厂商 / 间距 / 座型(翻盖 or 背夹) / 板端还是屏端 / 出处
   - 结尾"怎么用": 我们主板照这张表画座; 并写清**屏侧 40 针 → 主板侧 39 针的对应/合并关系**
2. `projects/smart_glasses/HW/PCB/display_39p_pinout.json`
   - `{"connector_model":"...","vendor":"...","pitch_mm":0.3,"positions":39,"source":"<URL>","pins":{"1":{"signal":"...","note":"...","source":"..."}, ... 39 项}}`
   - ★`pins` 必须 39 项齐全, 键是字符串脚号

## 查找路径 (按优先级, 都要试并记录结果)
1. ★**Radxa 官方文档站** `docs.radxa.com` / `wiki.radxa.com` 的 Display 8HD 页与附件
   —— ★**最可能落点**: Radxa 给 CM5 / Pi 5 / Rock 5 做的 **display 8HD 适配板/转接板**,
   那块板上就是 39p/0.3mm 的座 ⇒ ★**它的原理图 PDF = 主板侧针位表的权威出处**
2. Radxa **GitHub** 各 org (`radxa` / `radxa-docs` / `radxa-design` / `Radxa-*`) 里的硬件文件 (原理图 PDF / 硬件仓库)
3. 屏模组**随货原理图** (公开下载区)
4. Radxa 官方论坛/Discord 公开附件 (★只作补充, 不作唯一出处)

## 硬要求 (违反即交卷无效)
- ★**只认 Radxa 原厂资料** (官方 docs / 官方 GitHub / 原厂原理图 PDF); 第三方博客/论坛转述/AI 生成内容**不采信**
- ★**查不到就写"未查到"**, 并列出**试过的 URL + 失败原因**(403/404/无附件/需登录) ⇒ **绝对不许猜针位**
- 39 个脚**都要有出处**; 若原厂图只标信号名没标脚号 ⇒ 照抄信号并标"脚号按原图排布推定, 待核"
- **顺带取**: 那块适配板上用的 **39p/0.3mm 连接器型号**(我们要照它选型) + 是**翻盖(front flip)**还是**背夹(back flip)**
- **顺带确认**: 触控 I2C (TP_SCL/TP_SDA/TP_INT/TP_RESET) 与**背光 LED+/LED−** 在**主板侧**到底有没有、分别在哪几个脚
  ⇒ ★**若原厂排线只带 MIPI+电源 (不带触控/背光)** ⇒ 我们**必须自己做排线** ⇒ 这条结论要明确写出来
- **顺带确认**: 主板侧有没有把 40 针里的某些脚**并掉**(双 GND/双 LED 脚合成一个) ⇒ 列出"40→39 合并表"

## 纪律
- ★**只写上面这 2 个文件**; **不许改** 网表 / 板文件 / 规格 JSON / 脚本 / issue_log / tracker / STATE.yaml
- 临时下载全放 `/tmp/`; 不要塞进项目目录; 临时图片用完删
- 不发邮件 / 不联系厂家 / 不下单 / 不询价

## 验收标准
- [ ] `pins` 39 项齐全, 每项有 signal + source
- [ ] 连接器型号/厂商/间距/座型 有出处
- [ ] "40 针(屏侧) → 39 针(主板侧)" 的对应/合并关系讲清楚
- [ ] 触控与背光在主板侧的归属讲清楚 (带或不带)
- [ ] 查不到的部分明确标"未查到" + 试过的 URL 清单

## 汇报 (8~12 行)
39 项取到几项 / 连接器型号 / 40→39 合并关系 / 触控与背光在不在主板侧 / 未查到的清单 / 两个文件路径
