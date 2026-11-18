#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0745_open_iss237_p2_panel.py
★main (moli) 新开 ISS-237 (P2 屏口径收死 + 残留清账) · 2026-11-16 07:5x (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮 main 自己实跑, 不抄任何交卷报告★)** ★★
· ★**本轮 advance.py 的 internal 段是空的** (三个总工各有 1 条 fixing 单在飞 + 各有 3 条写会话在跑) ⇒ **本轮一条都派不出去**
· ★**但 main 自己逐行读盘时挖出一条【主线内·原理图/网表口径】的真矛盾** ⇒ 按 INFLIGHT_20261115.md ④ 的口径
  (★owner=main 名下的选型类 open 单 ISS-172 / ISS-156 可考虑改派 hw-lead★) ⇒ ★**先开单 + 写好 brief, 等 hw-lead 名额空出来直接派** ★

★★**ISS-237 的实证 (★全部是 main 本轮 07:4x 实测, 行号可复核★)** ★★
① ★**同一份文件里两套 P2 屏口径并存**:
   · `HW/STEP1_PARTS_SPEC.md` §0 (L15~31) 表格 = ★**P2 = Radxa Display 8 HD (800×1280)** + 主板照抄 **40p/0.5mm**★
   · 同文件 §3 (L190~) 整节 = 8 HD + §3.1 **全 40 针原文** + §3.3 背光 **12V 级** (10FHD typ 12.8V / max 14V @200mA)
   · 同文件 §5 落成约束 **M6 = 屏背光单独一路 12V BOOST + 限流**
   · 同文件 §6 **S1 (L414) = 「display 22p/0.5mm (逐针表 22/22) …『display 40p』是视涯屏期 (0.49" 39/40p) 残留, 随视涯屏 11-04 停用一并作废 (老板 11-11 19:31 裁决: 以【实际接插件】的针数为准)」** ★
   ⇒ ★**§0 是「一句话结论」= 最容易被照抄的那一段, 它和 §6 S1 互相打脸** ★
② ★**现行网表/脚表站在 22p 这一边**:
   · `HW/netlist_v1.csv` CONN_LIGHT = ★**22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 针序照 Pi5 官方 J4)**★ (513 行)
   · `HW/netlist_v1_pins.csv` (585 行) 里 count(ref==CONN_LIGHT) == **22** · count(ref==CONN_CAM) == **31**
   · ★**网表里没有 12V/背光/BOOST 那一路** ⇒ grep `12V|BOOST|BL_` 在 `HW/netlist_v1.csv` 只命中 1 行, 且那行是 OTG_SET 的 note 里出现 "boost" 字样, **不是背光轨** ★
③ ★**落成约束 M6 是照 §3 (8HD/10FHD) 写的** ⇒ M6 这条「待落表」项一旦被当成活项执行 ⇒ 网表会多出一路不存在的 12V BOOST
④ ★**现行口径真源是 `HW/PCB/FPC_PIN_TABLES.md`** (camera = Radxa Camera 4K 31p/0.3mm FH35C-31S-0.3SHW(50) · display = Waveshare 2.8inch DSI LCD SKU 22028, 官方线 22p(0.5mm Pi5 侧)↔15p(1.0mm 屏侧), 座 FH12-22S-0.5SH(55))

★★**风险 (为什么不能拖)★★ ★★
· 有人照 §0/§3 画板/落表 ⇒ 画 40p 座 + 加 12V BOOST ⇒ 而板/网表是 22p ⇒ ★**投板前返工** ★
· M6 这条落成约束级条目会被当成「待落表项」⇒ ★**落表批次会带进一个不存在的轨** ★
· demo 屏到底用哪块 (A 维持 22p / B 换 8 HD 40p) ★**现在是三份文档各说各话** ⇒ 画板的人没有单一事实源 ★

★★**边界 (本单)★★ ★★
★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到写降级方案
★**不许改网表/脚表/BOM/板** (★本单只出结论 + 对账 + 门禁 + 作业包; 落表并进下一次落表批次, 避免与 ISS-236 的一键落表器撞车★)
★**不许碰 PCB 布线/布局/板框** (板那一趟继续排队) ★**不许替老板拍屏版本** (决策页 §A6)
★**不改 PROJECT_TRACKER.md §0** · ★**不写别人的分片** · ★**不发邮件 / 不联系供应商 / 不下采购单** ★
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

TITLE_237 = (
    "★★[主线内·原理图/网表侧·内部活] ★**P2 屏口径自相矛盾** (STEP1_PARTS_SPEC.md §0/§3 = 40p/8HD/12V BOOST "
    "vs §6 S1 + 现行网表 = 22p/Waveshare 2.8\") ⇒ 收死 P2 + 清残留 + M1~M11 落成约束 × 网表逐条对账 + 机器门禁"
)

DESC_237 = (
    "★main 2026-11-16 07:4x 自己逐行实跑出来的 (★不是抄任何交卷报告★) ⇒ ★**同一份主线文档里两套 P2 屏口径并存, 而现行网表/脚表/板站在第三种口径上** ★\n"
    "★**① 文档内自相矛盾 (行号可复核)**: ★\n"
    "· `HW/STEP1_PARTS_SPEC.md` ★**§0 (L15~31) 的表格** = 「P2 屏模组 = ★**Radxa Display 8 HD (800×1280)**★ · 主板要照抄的关键规格 = ★**40p / 0.5mm** FPC」 ★\n"
    "· 同文件 ★**§3 (L190 起) 整节** = 8 HD, §3.1 = 「全 40 针原文」 (屏侧 40p/0.5mm · 主板侧 39p/0.3mm 或 15p/1.0mm), §3.3 = 背光「12V 级」(10FHD typ 12.8V / max 14V @200mA typ) ★\n"
    "· 同文件 ★**§5 落成约束 M6** = 「屏背光单独一路 12V BOOST + 限流」★\n"
    "· 同文件 ★**§6 S1 (L414)** = 「★**display 22p/0.5mm (逐针表 22/22)** … ★**『display 40p』是视涯屏期 (0.49\" 39/40p) 残留, 随视涯屏 11-04 停用一并作废 (★老板 11-11 19:31 裁决: 以【实际接插件】的针数为准★)**」★\n"
    "⇒ ★**§0 是「一句话结论」= 最容易被照抄的那一段, 它与 §6 S1 直接打架; 而 §3 的 40 针表 / 12V 背光 / M6 三件都建立在 40p 这一侧** ★\n"
    "★**② 现行真源站在 22p 这一侧 (main 实测)**: ★\n"
    "· `HW/netlist_v1.csv` (513 行) CONN_LIGHT = ★**22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)**, 针序照 Pi5 官方 J4 ★\n"
    "· `HW/netlist_v1_pins.csv` (585 行): count(ref==CONN_LIGHT) == ★**22**★ · count(ref==CONN_CAM) == ★**31**★ ★\n"
    "· ★**网表里没有 12V/背光/BOOST 那一路** ⇒ grep `12V|BOOST|BL_` 在 `HW/netlist_v1.csv` 只命中 1 行, 且那行是 OTG_SET 的 note 里出现 \"boost\" 字样, 不是背光轨 ★\n"
    "· 现行口径真源 = `HW/PCB/FPC_PIN_TABLES.md` (camera = Radxa Camera 4K 31p/0.3mm, 座 FH35C-31S-0.3SHW(50) · display = Waveshare 2.8inch DSI LCD SKU 22028, 官方线 22p(0.5mm Pi5 侧)↔15p(1.0mm 屏侧), 座 FH12-22S-0.5SH(55)) ★\n"
    "★**③ 风险 (★为什么不能拖到板那一趟★)**: ★\n"
    "· 谁照 §0/§3 去画板/落表 ⇒ 画 40p 座 + 加一路 12V BOOST ⇒ 而板/网表是 22p ⇒ ★**投板前返工** ★\n"
    "· M6 是「落成约束」级条目 ⇒ 会被当成待落表项 ⇒ ★**落表批次里会带进一个不存在的轨** ★\n"
    "· demo 屏到底用哪块 (维持 22p / 换 8 HD 40p) ★**现在三份文档各说各话 ⇒ 画板的人没有单一事实源** ★\n"
    "★**④ 本单要做的事**: ★**① P2 口径裁定 (只列选项 + 依据, 不替老板拍屏版本) ② §0/§3/§5/§6 的残留清账 (加标记不改实测原文) ③ 新增 §7「M1~M11 落成约束 × 现行网表」逐条对账表 ④ 机器门禁 (新建脚本 + --selftest) ⑤ 交付物 4 件 + 分片** ★\n"
    "★**本单不许落表 (★不许改网表/脚表/BOM/板★)** ⇒ 落表并进下一次落表批次, ★避免与 ISS-236 的一键落表器撞车★ ★"
)

BRIEF_237 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**P2 屏口径收死成单一事实源**★ ⇒ ★**同一份主线文档里不许再有两套屏口径并存**★ ⇒ ★**出裁定 + 残留清账 + M1~M11 落成约束 × 现行网表逐条对账表 + 一个能自动复核的机器门禁**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 07:4x 自己实跑, 不是推测★)** ★★
· ★**本轮 advance.py 的 internal 段是空的** (三个总工各有 1 条 fixing 单在飞 + 各有 3 条写会话在跑) ⇒ ★**你这条是 main 逐行读盘时挖出来的真矛盾, 不是「等下一轮再说」** ★
· ★**矛盾本体 (★行号可复核★)**: `HW/STEP1_PARTS_SPEC.md` ★**§0 (L15~31)** 说 P2 = Radxa Display 8 HD + 主板照抄 ★**40p/0.5mm**★ · ★**§3 (L190 起)** = 8 HD + 全 40 针原文 + 背光 12V 级 · ★**§5 M6** = 屏背光单独一路 12V BOOST + 限流 · ★**§6 S1 (L414)** 说 display = ★**22p/0.5mm**★ 且「display 40p 是视涯屏期残留, ★**随视涯屏 11-04 停用一并作废** (老板 11-11 19:31 裁决: 以【实际接插件】的针数为准)」
· ★**现行真源站在 22p 这一边**: `HW/netlist_v1.csv` CONN_LIGHT = 22p@0.5mm (FH12-22S-0.5SH(55), 针序照 Pi5 J4) · `HW/netlist_v1_pins.csv` count(CONN_LIGHT) == 22 · count(CONN_CAM) == 31 · ★**网表里没有 12V/背光/BOOST 那一路** (grep `12V|BOOST|BL_` 只命中 1 行 OTG_SET 的 note 字样)
· ★**后果**: 照 §0/§3 画板 ⇒ 画 40p 座 + 加 12V BOOST ⇒ 而板/网表是 22p ⇒ ★**投板前返工** ★; M6 会被当成待落表项 ⇒ ★**落表批次带进一个不存在的轨** ★

★★**① P2 口径裁定 (★只出结论 + 依据, 不替老板拍★)** ★★
· ★**必须给两条并列候选 (★不许只写一条★)**, 每条逐项给齐: ★**① 屏型号与实物 ② 主板座规格 (针数/间距/座型号) ③ 背光/供电增量 (含要不要新增 12V BOOST 这一路) ④ 网表改动面 (★行数 + 脚数 + 要不要改 CONN_LIGHT/CONN_CAM 的器件行★) ⑤ 驱动路线 (★`simple-panel-dsi` vs 私有 panel driver★) ⑥ 风险 + 降级方案 ⑦ 证据等级 + 出处 (★[官网]/[实测]/[媒体]/[推算]/[0数据]★)** ★
· ★**候选 A (★维持现行口径★)** = Waveshare 2.8inch DSI LCD (SKU 22028) · 官方线 22p(0.5mm Pi5 侧)↔15p(1.0mm 屏侧) · 座 FH12-22S-0.5SH(55) ⇒ ★**网表/脚表/板/BOM 一格都不动** ★
· ★**候选 B (★换 Radxa Display 8 HD★)** = 800×1280 · 屏侧 40p/0.5mm · 主板侧 39p/0.3mm 或 15p/1.0mm ⇒ ★**座要改 22p→40p (网表 + 脚表 + BOM + 板同批) + 背光 12V ⇒ 主板要加一路 BOOST** ★
· ★**★不许替老板拍屏版本★** (★决策页 §A6 的全彩版/单色绿版是整机阶段的事★) ⇒ ★**只给「demo 板用哪块」的推荐 + 依据, 并标明这是 main 级选型待签** ★

★★**② 残留清账 (★★不许改实测原文★, 只许加标记★)** ★★
· ★**`HW/STEP1_PARTS_SPEC.md` §0 顶部加一条裁定横幅** (★写清: 以哪条为准 + 为什么 + 单号 ISS-237 + 裁定日期★) ⇒ ★**§0 是最容易被照抄的那一段, 横幅必须落在 §0 最前面** ★
· ★**§3 的每条与裁定冲突的项加「★已作废 (依据 ISS-237 …)★」标记** ⇒ ★**实测原文 (40 针表 / 12V 背光 / 39p/15p) 一字不许删改, 只许加标记** ★
· ★**§5 M6 按裁定改判定** (★作废 / 待落表, 二选一并写理由★) · ★**§6 S1 补一句「本条经 ISS-237 确认为准」** ★
· ★**`HW/PART_ALTERNATIVES_REGISTRY.md` §3 / §5 同步口径** (★只许改口径栏与「已作废/现行」标注, ★不许改实测数据/链接★)

★★**③ §7 新增对账表 (★M1~M11 逐条, 一条都不许空★)** ★★
· 表格列: ★**条目号 (M1~M11) · 约束原文摘要 · 判定 (★已落表 / 待落表 / 已作废(理由) / 待老板拍★) · 证据 (★网表行号 或 脚表计数, 要具体★) · 落表批次 (★V-2/V-3/V-4 同批 / 板那一趟 / 不落★)** ★
· ★**11 行必须齐全** (★缺一行 ⇒ 门禁红★) · ★**每行的判定必须能被机器复核** (★不许写「基本已落」这种话★) ★
· ★**§5 里没写进 M1~M11 的其它落成约束也要列一行** ⇒ ★**表头写清「本表是 §5 全部落成约束的对账, 不止 M1~M11」** ★

★★**④ 机器门禁 (★本单必须留一个能自动复核的东西★)** ★★
· ★**新建★ `HW/check_step1_parts_spec.py` ⇒ 至少查: ①**文档里 display 座的有效口径只有一种 (★40p 与 22p 不许同时被标「现行/有效」★) ②**现行网表 CONN_LIGHT 的脚数 == 裁定后口径 (★读 `HW/netlist_v1_pins.csv` 计数, 不许硬写 22★) ③**网表里存在/不存在 12V BOOST 那一路, 与裁定一致 ④**对账表行数齐全 + 每行判定非空 + 允许的判定词只有那四个 ⑤**`HW/PCB/FPC_PIN_TABLES.md` 的 display 口径 == 裁定口径 ★
· ★**rc=0 = 全过; 任何一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**必须支持 `--selftest` (★至少 5 个用例: 改坏 §0 针数 / 删掉 S1 / 改网表脚数 / 删一条对账判定 / 把 M6 判定改成非法词 ⇒ 全都要被抓★)** ★
· ★**不许改** `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/FPC_PIN_TABLES.md` · `HW/PCB/PI5_DSI_22P_PINOUT.md` (★md5 一个都不许变★) · ★**不许改** `HW/SCHEMATIC_LANDING_V1_LANDED.md` 与 `state/gen_netlist.py` (★那是 ISS-233/ISS-236 的地界★)

★★**⑤ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**改** `HW/STEP1_PARTS_SPEC.md` (★§0 裁定横幅 + §3 作废标记 + §5 M6 判定 + §6 S1 补注 + ★**新增 §7 对账表**★)
2. ★**改** `HW/PART_ALTERNATIVES_REGISTRY.md` (★只改 §3 / §5 的口径栏与作废标注★)
3. ★**新建★ `HW/check_step1_parts_spec.py` (★门禁 + `--selftest`★)
4. ★**新建★ `HANDOFF/2026-11-16_hw-lead_ISS237_P2屏口径收死与残留清账.md` (★≤25 行, B1~B6 六块齐全★)
5. `state/fragments/hw.yaml` (★走 `state/frag_write.py` 原子写: 只加 artifact/claim/answer; ★**不许删改别人的 key**★)

★★**⑥ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 HW/check_step1_parts_spec.py` ⇒ **rc=0** 且逐项 PASS
· `python3 HW/check_step1_parts_spec.py --selftest` ⇒ **rc=0**, **≥5/5** 用例
· `HW/STEP1_PARTS_SPEC.md` ★**§0 顶部有裁定横幅 + §7 对账表齐全 (M1~M11 一条不缺, 每行判定非空且是那四个词之一)★**
· ★**文档里不许同时出现「display = 40p/0.5mm」与「display = 22p/0.5mm」两个被标成现行/有效的说法★**
· `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb` ⇒ ★**与交卷前逐字节一致 (34132f7e… / b21b743a… / c195a117… / 611b869e…)** ★
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· ★**零外发** · ★**实物 [实测] = 0 条** (★板不在本机★) · ★**没碰 PCB 布线/布局/板框** · ★**没改 PROJECT_TRACKER.md §0** · ★**没改 issue_log (verify_by = main)** ★

★★**⑦ 额外纪律 (★踩过的坑别再踩★)** ★★
· ★**「有断言」不等于「断言有效」** ⇒ ★**每条反向用例必须自证「它真的改到了目标」, 否则就是一条永远绿着的假用例 (★ISS-227 同款教训★)** ★
· ★**不许把「已作废」的旧口径直接删掉** ⇒ ★**删掉 = 失去「当初为什么这么选」的留痕; 标记作废才是正解 (★本项目的判据本体只许加不许放宽★)** ★
"""


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {it.get("id"): it for it in issues}

    assert "ISS-237" not in by_id, "ISS-237 已存在, 不重复开"

    # ---------------- 新开 ISS-237 (hw-lead) ----------------
    issues.append({
        "id": "ISS-237",
        "title": TITLE_237,
        "severity": "high",
        "source_blocker": None,
        "desc": DESC_237,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": BRIEF_237,
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-16 07:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 07:4x 自己实跑** "
            "(逐行读 `HW/STEP1_PARTS_SPEC.md` §0/§3/§5/§6 + `HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 计数 + "
            "`HW/PCB/FPC_PIN_TABLES.md` + 4 个受保护 md5 实测) ★\n"
            "★**本轮 advance.py internal 段为空 (三个总工各有 fixing 单在飞 + 各有写会话在跑) ⇒ 本轮没派出任何一条; "
            "本单按 INFLIGHT_20261115.md ④ 的口径先开单备料, 等 hw-lead 名额空出来直接派** ★\n"
            "★**这单是主线内 (原理图/网表/选型口径类), 一条 PCB 布线/布局都不碰** ★\n"
            "★**本单不许落表 (不许改网表/脚表/BOM/板) ⇒ 避免与 ISS-236 的一键落表器撞车** ★\n"
            "★**零外发** · ★**未替老板拍屏版本 (决策页 §A6)** ★"
        ),
        "dispatched_at": None,
    })

    # 备份 + 原子写
    bak = os.path.join(HERE, f"issue_log.yaml.bak_20261116_0745_open_iss237")
    shutil.copy2(LOG, bak)

    with open(LOG, encoding="utf-8") as f:
        pass
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))

    # 派活备料 (下一轮 dispatcher 直接用)
    task_md = os.path.join(HERE, "tasks", "advance_iss237.md")
    atomic_write(task_md, BRIEF_237)

    print(f"✅ ISS-237 已开 (owner=hw-lead, status=open, due=2026-11-19)")
    print(f"   备份: {bak}")
    print(f"   备料: {task_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
