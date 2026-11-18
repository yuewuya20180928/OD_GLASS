#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-277 / ISS-292 · 生成 HW/PCB/BOARD_ONEPASS_PREFLIGHT.md (★页 + JSON 块同源 ★)

★★【ISS-292 · 2026-11-17 · hw-lead】生成器与盘面页对齐 (★跑一次不许把订正冲掉★)★★

★**本生成器的三条铁律 (★ISS-292 的全部意义就在这三条★)** ★★

① ★**现状值一律从真源读, 一律不许写死** ★★
   - `R3-A4` 三个数 (★MAIN_PCB且DNP / 在板上 / 零标记★) ⇒ 读 `HW/check_netlist_contradiction_r3.py` 的实跑输出
   - 脚表缺陷条数 (★总数 / 功能缺陷 / 串号 / 缺脚 / md5 台账对账★) ⇒ 读 `HW/check_pin_function_labels.py` 的实跑输出
   - 「上一次 DNP 变动的落表事件」⇒ 读落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md`
   ⇒ ★**下次落表 / 动板之后, 跑一次生成器就是新值, 不必人来改★ ★★

② ★**追加式订正块不许被重跑冲掉** ★★
   ⇒ 两块追加式内容 (★ISS-283 的 §3-追加 §③-1~§③-3 / ISS-289 的 §附录 + `state_baseline` 登记表★)
   存在 sidecar `state/_iss277_preflight_appendix.md` ⇒ ★**生成器只做搬运, 不改一个字★ ★★

③ ★**页与 JSON 同源** ★★
   ⇒ §2 表格行与 §7 JSON 条目由同一份 `ITEMS` 生成 (★例外: 3 条 ISS-283 手工订正过的表格行
     走 `TABLE_ROW_OVERRIDES` 原样保留 ⇒ 老字一字未删★) ★★

★**用法** ★
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    python3 state/_iss277_build_preflight.py          # ★重跑 = 幂等 (★跑前后页 md5 逐字节相同★) ★

★**边界** ★: ★零写板 · 零落表 · 只写 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 一个文件★ ★★
"""
import json
import os
import re
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
OUT = os.path.join(PROJ, "tmp", "iss292_sbx", "gen_out.md")

# ★★追加式订正块 sidecar (★ISS-292 新增·★生成器的第二个输入★) ★★
APPENDIX_REL = "state/_iss277_preflight_appendix.md"
APPENDIX = os.path.join(PROJ, APPENDIX_REL)

# ★★落表台账 (★DNP 落表事件的出处★) ★★
LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"


# ==============================================================================
# 真源读数 (★铁律 ①★)
# ==============================================================================
def run(cmd, timeout=900):
    r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace")


def read_r3_a4():
    """★R3-A4 三个数 ⇒ (MAIN_PCB且DNP, 在板上, 零标记) ★

    ★**真源 = `HW/check_netlist_contradiction_r3.py` 的实跑输出** (★不许自己重算一套·那会与闸脱钩★) ★
    """
    rc, out = run(["python3", "HW/check_netlist_contradiction_r3.py"])
    m = re.search(r"R3-A4: MAIN_PCB且DNP (\d+) 颗 · 在板上 (\d+) 颗 · 零标记 (\d+) 颗", out)
    if not m:
        raise SystemExit("★读不到 R3-A4 (★rc=%d★) ⇒ 拒写页 (★fail-closed·不许猜★)\n%s"
                         % (rc, out[-2000:]))
    return tuple(int(x) for x in m.groups())


def read_pins_defects():
    """★脚表缺陷条数 ⇒ dict(total, functional, wrong, missing, md5) ★

    ★**真源 = `HW/check_pin_function_labels.py` 的实跑输出** ★
    ★- total     = 判定行的「N 条缺陷」(★计入 rc 的总条数★)
    ★- functional= 缺陷清单段的「共 N 条」(★脚表功能缺陷·串号 + 缺脚★)
    ★- wrong     = 缺陷清单段里 `[WRONG_FUNCTION]` 的条数 (★串号★)
    ★- missing   = 缺陷清单段里 `[MISSING_PIN]` 的条数 (★缺脚★)
    ★- md5       = `[MD5_CHANGED]` 的条数 (★落表后基线过期的台账对账条数★)
    """
    rc, out = run(["python3", "HW/check_pin_function_labels.py"])
    mt = re.search(r"\((\d+) 条缺陷\)", out)
    mf = re.search(r"【缺陷清单 \(★计入 rc·共 (\d+) 条★\)】", out)
    if not mt or not mf:
        raise SystemExit("★读不到脚表缺陷条数 (★rc=%d★) ⇒ 拒写页 (★fail-closed·不许猜★)\n%s"
                         % (rc, out[-2000:]))
    seg = out.split("【缺陷清单", 1)[1].split("【提示", 1)[0] if "【缺陷清单" in out else ""
    d = {
        "total": int(mt.group(1)),
        "functional": int(mf.group(1)),
        "wrong": seg.count("[WRONG_FUNCTION]"),
        "missing": seg.count("[MISSING_PIN]"),
        "md5": out.count("[MD5_CHANGED]"),
    }
    if d["wrong"] + d["missing"] != d["functional"]:
        print("★⚠ 脚表缺陷段自相矛盾: 串号 %d + 缺脚 %d ≠ 功能缺陷 %d ⇒ 按功能缺陷 %d 写★"
              % (d["wrong"], d["missing"], d["functional"], d["functional"]))
    return d


_CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
           "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def read_dnp_landing_event():
    """★落表台账里最近一次「删了 N 行 DNP」的落表 ⇒ (时间, V-标签, N) 或 None ★

    ★**真源 = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的每条落表链** ★
    ★- 时间   = 链头的「落表时间」行
    ★- V-标签 = 该链的拍板表里那一行的 V 值与取值 (★如 `V-3=E`★)
    ★- N      = 落点列里「删 DEMO_DNP N 行」的中文数字 (★如 三 ⇒ 3★)
    ★★**只认台账里写着的「删 DEMO_DNP N 行」这一种落法** ★★
    (★★它就是「3 颗 BAT_DET 从 DNP 改成必装」那件事的唯一书面出处★) ★★
    """
    path = os.path.join(PROJ, LEDGER_REL)
    if not os.path.exists(path):
        return None
    lines = open(path, encoding="utf-8").read().split("\n")
    heads = [i for i, l in enumerate(lines) if re.match(r"^##\s+", l)]
    found = None
    for k, s in enumerate(heads):
        e = heads[k + 1] if k + 1 < len(heads) else len(lines)
        blk = "\n".join(lines[s:e])
        mt = re.search(r"落表时间\*\*:\s*★\*\*([\d\-]+ [\d:]+) \(Asia", blk)
        md = re.search(r"删 DEMO_DNP ([一二三四五六七八九十]+)行", blk)
        if not mt or not md:
            continue
        mv = re.search(r"\|\s*★\*\*V-(\d+)\*\*\s*★\s*\|\s*★\*\*([^★]+)\*\*\s*★", blk)
        n = _CN_NUM.get(md.group(1))
        if not n:
            continue
        found = (mt.group(1), ("V-%s=%s" % (mv.group(1), mv.group(2).strip())) if mv else "?", n)
    return found


def read_appendix_blocks():
    """★读 sidecar 的两块追加式订正 ⇒ (s3_text, iss289_text, baseline_dict) ★

    ★**sidecar 缺 ⇒ 拒写页 (★fail-closed★)**: 追加式订正块是「老字不许删」的载体,
    ★**丢了它 = 重跑一次就把 ISS-283 / ISS-289 的订正全冲掉** ⇒ 宁可报错也不许悄悄少一块★ ★★
    """
    if not os.path.exists(APPENDIX):
        raise SystemExit("★sidecar %s 不存在 ⇒ 拒写页 (★fail-closed·追加式订正块不许丢★)"
                         % APPENDIX_REL)
    txt = open(APPENDIX, encoding="utf-8").read()

    def block(tag):
        m = re.search(r"<!-- ISS292:%s:BEGIN -->\n(.*?)<!-- ISS292:%s:END -->"
                      % (tag, tag), txt, re.S)
        if not m:
            raise SystemExit("★sidecar 里读不到 %s 块 ⇒ 拒写页 (★fail-closed★)" % tag)
        return m.group(1).rstrip("\n").split("\n")

    s3 = block("S3_APPENDIX")
    app = block("ISS289_APPENDIX")
    # ★批次基线 (★ISS-289 那批登记的脚表功能缺陷条数★) ⇒ 从附录的 state_baseline 里读
    baseline = {}
    for m in re.finditer(r"```json\s*\n(\{.*?\n\})\s*\n```", txt, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(d, dict) and "state_baseline" in d:
            for e in (d["state_baseline"].get("entries") or []):
                if e.get("id") == "C06_B03_DEFECT_COUNT":
                    mm = re.search(r"脚表 \d+ 条缺陷 = (\d+) 条脚表功能缺陷", str(e.get("anchor", "")))
                    if mm:
                        baseline["pins_functional"] = int(mm.group(1))
    return s3, app, baseline


def build_tokens():
    """★★把真源读数变成模板占位符 (★铁律 ①★) ★★"""
    t, o, z = read_r3_a4()
    pins = read_pins_defects()
    ev = read_dnp_landing_event()
    _, _, baseline = read_appendix_blocks()

    # ★R3-A4 的落表事件注记 (★三个数全部随落表变, 变的是颗数不是性质★) ★
    if ev:
        at, vlabel, n = ev
        note = ("%s 落表 %s 删了 %d 行 DNP ⇒ %d/%d/%d → %d/%d/%d, "
                "★本条 3 个数全部随落表变, 变的是颗数不是性质★"
                % (at, vlabel, n, t + n, o + n, z + n, t, o, z))
    else:
        note = ("★本条 3 个数全部随落表变, 变的是颗数不是性质★ "
                "★⚠ 落表台账里【读不到「删了 N 行 DNP」的落表事件】⇒ 注记降级 (★fail-soft★)★")

    # ★脚表缺陷条数的注记 ★
    md5_note = "(★落表后基线过期★)" if pins["md5"] else ""
    base_f = baseline.get("pins_functional")
    if base_f is None:
        f_note = "脚表功能缺陷条数 (★ISS-289 那批的基线读不到★), "
    elif base_f == pins["functional"]:
        f_note = "脚表功能缺陷本批未变, "
    else:
        f_note = "脚表功能缺陷本批已变 (★ISS-289 那批是 %d 条★), " % base_f

    return {
        "«R3_T»": str(t), "«R3_O»": str(o), "«R3_Z»": str(z), "«R3_NOTE»": note,
        "«P_T»": str(pins["total"]), "«P_F»": str(pins["functional"]),
        "«P_W»": str(pins["wrong"]), "«P_M»": str(pins["missing"]),
        "«P_MD5»": str(pins["md5"]), "«P_MD5_NOTE»": md5_note, "«P_F_NOTE»": f_note,
    }


def subst(text, tokens):
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


# ==============================================================================
# 条目 (★id, source_iss, title, current_state, action, criterion, step, blocked_by, evidence★)
# ==============================================================================
# ★★真源读数 (★铁律 ①★) ⇒ 现状值占位符 ★★
TOKENS = build_tokens()
print("★真源读数:", TOKENS)

# ★★条目本体 (★现状值里的 @@…@@ 占位符一律由真源读数替换·★不许写死★) ★★
ITEMS_RAW = [
 ("B01_REF_SUFFIX", "ISS-266",
  "186 个封装位号加 _1 数字后缀 (KiCad 问号根因)",
  "[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号 (HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md §0/§2/§4)",
  "改 HW/SCHEMATIC_V1_SPEC.json 的 186 个 ref + state/gen_kicad_sch.py 三处同步; 板侧 186 个封装位号随 S6 重出自动带",
  "python3 HW/check_step1_parts_spec.py ⇒ rc=0 (问号行数=0 · 218 位号两两不重名)",
  "S1", "-", "[实测]"),
 ("B02_C_VBUS_GND", "ISS-266",
  "C_VBUS_GND 从 demo 主 PCB 拿掉 (B-1)",
  "[实测] 板上仍在, 且它当下两个带网焊盘挂的是: C_VBUS_GND pad1 = GND / C_VBUS_GND pad2 = VBUS_5V_CHG ⇒ 焊盘级多余 2",
  "重出板时按网表 board 列过滤 (网表两行已改判 CHG_BOARD) ⇒ 该封装自动消失; 不许手改板",
  "bash state/pcbnew_py.sh state/check_pcb_nets.py ⇒ C1 缺失 0 · 多余 0 (现状: 多余 2)",
  "S2", "-", "[实测]"),
 ("B03_ULDO_S28_PAD3", "ISS-239",
  "U_LDO_S28 缺 pin3(EN) ⇒ 若走 A 案板须补 pad3",
  "[实测] 脚表 «P_T» 条缺陷 = «P_F» 条脚表功能缺陷 («P_W» 串号 + «P_M» 缺脚) + «P_MD5» 条 md5 台账对账 «P_MD5_NOTE»; U_LDO_S28 无 pin3 行 ⇒ 板侧无 pad3 ⇒ 焊盘级恰 1 颗不等价",
  "A 案: 板侧给 U_LDO_S28 补 pad3 + 脚表补行; B 案: 不补 (本单不代拍)",
  "python3 HW/check_pin_function_labels.py --expect-known ⇒ rc=0 (★现状: «P_T» 条缺陷 = «P_F» 脚表功能 («P_W» 串号 + «P_M» 缺脚) + «P_MD5» md5 台账对账; ★«P_F_NOTE»多出的 «P_MD5» 条是落表后基线过期 (KNOWN_DEFECTS 快照同步归 ISS-283)★)",
  "S2", "老板/PM 拍 A/B 案 (ISS-239 §4.2)", "[实测]"),
 ("B04_R_SUPV_DIV_DNP", "ISS-244",
  "R_SUPV_DIV1/2 = 0Ω 且 dnp=必装, 而 U_SUPV dnp=DNP ⇒ 装 0Ω 等于把 V_SOC_IO 短到地",
  "[实测] 网表: R_SUPV_DIV1 / R_SUPV_DIV2 的 dnp=必装 且 value=0Ω 跳线; U_SUPV 三行 dnp=DNP",
  "落表批次把 R_SUPV_DIV1/2 一并置 DNP (随 U_SUPV) ⇒ 零成本; 不许在板侧硬改",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)",
  "S2", "落表批次 (V-3 归老板 A1)", "[实测]"),
 ("B05_U_EN_SW_VALUE", "ISS-269",
  "板封装 U_EN_SW 的 Value 属性陈旧 (B-2)",
  "[实测] 板封装 Value = 'EN 输入 (高=放行底板)' (脚功能串, 不是器件身份)",
  "生成器侧 B-2 已修 (ISS-269) ⇒ 重出板自动刷成含 TPS22991RAA 的器件身份",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference()=='U_EN_SW'])\" ⇒ 值含 TPS22991RAA",
  "S3", "-", "[实测]"),
 ("B06_TPS7A20_VALUE", "ISS-239",
  "7 颗 TPS7A20 的板封装 Value 同为脚功能串 (与 B05 同根因)",
  "[实测] 板上 7 颗 LDO 的 Value = 'EN (pin3)' / 'GND (pin2)' ⇒ 贴片程序里没有 TPS7A20-33 这个料号",
  "同 B05 一批刷 (生成器本体行优先 ⇒ 板上 22 个封装 Value 一并刷新)",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([f.GetValue() for f in b.GetFootprints() if f.GetReference().startswith('U_LDO_')])\" ⇒ 7 颗都含 TPS7A20",
  "S3", "-", "[实测]"),
 ("B07_ESD_USB_D_3PIN", "ISS-266",
  "D_ESD_USB_D 从 2 脚换 3 脚封装 (B-3)",
  "[实测] 板上是 2 脚占位 (pad1 / pad2)",
  "落点 = state/gen_pcb_components.py 封装表 + state/gen_pcb_netlist_board.py 的 make_footprint 分派 ⇒ pad1=D+ / pad2=D− / pad3=GND",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D_ESD_USB_D 焊盘数 = 3",
  "S4", "W-1/W-2 (老板: 一颗双通道 vs 两颗单通道)", "[实测]"),
 ("B08_ESD_USB_D_NEAR", "ISS-266",
  "D_ESD_USB_D 距 J_USB_C 47.99 mm (B-4)",
  "[实测] D_ESD_USB_D @ (94.95, 21.8) · J_USB_C @ (140.00, 5.25) ⇒ 中心距 47.99 mm (要求 ≤ 3.0 mm)",
  "用 PCB_PART_POS 钉位到 J_USB_C 旁 ≤ 3.0 mm (不许手改板坐标)",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R9: D_ESD_USB_D ↔ J_USB_C 中心距 ≤ 3.0 mm",
  "S4", "W-1/W-2 (老板)", "[实测]"),
 ("B09_ESD_USB_D_MINUS", "ISS-266",
  "USB D− 那条路没有 ESD (B-5)",
  "[实测] 板上挂 USB_D_N_SRC / NET_USB_D_N_TYPEC 的 ESD 位号数 = 0",
  "B-3 做完自然满足 (换 3 脚后同时挂 D−); 或新增位号 D_ESD_USB_N (落表侧另派)",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4: D− 两张网的 ESD 位号数 ≥ 1",
  "S4", "落表侧另派 (B-5 两条路都要改网表)", "[实测]"),
 ("B32_V2_NET_RENAME", "ISS-283",
  "V-2 网改名: D_ESD_USB_D pad1 网名 USB_D_P_SRC → NET_USB_D_P_TYPEC ⇒ 板面 3 处焊盘网名必须同趟改 (★§③-1★)",
  "[实测] 网表 L417 已落 NET_USB_D_P_TYPEC (★台账 §16.2 链头 L1353 · ISS-283 · 12:16:08★); 板面仍挂旧网名 USB_D_P_SRC 的焊盘 3 处: D_ESD_USB_D.pad1 / R_SER_USB_D_P 一端 / J_SOM_P1 的 USB_D_P 脚 ⇒ 网表与板对不上",
  "板那一趟把这 3 处焊盘网名同趟改成 NET_USB_D_P_TYPEC (★不改 ⇒ 网表与板对不上★) ⇒ 见板侧清单 §③-1; ★本单零写板★",
  "python3 HW/check_board_frame_caliber.py ⇒ C6 绿 (★盘上 md5 == 落表台账登记★)",
  "S4", "板只改一次那一趟 (★本单零写板★)", "[实测]"),
 ("B10_Q_AND_LAND", "ISS-244",
  "Q_AND 占位 land 的 pad↔pin 与器件引脚序对不上 (硬件 AND 门不成立)",
  "[实测] 板: pad1=RESET_N(D) / pad2=GND(S) / pad3=PG_AND(G) = D/S/G; AO3400A 引脚序 = 1=G / 2=S / 3=D ⇒ 装上去 = 栅极接 RESET_N、漏极接 PG_AND",
  "land 目标 = pad1=PG_AND(G) / pad2=GND(S) / pad3=RESET_N(D) (两个外侧 pad 对调) ⇒ 改 make_footprint 的 pin↔net 映射",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_AND'][0].Pads()])\" ⇒ pad1 挂 PG_AND / pad3 挂 RESET_N",
  "S6", "落表批次 (AO3400A 已落)", "[实测]+[官网]"),
 ("B11_Q_PG_LAND", "ISS-244",
  "Q_PG 占位 land 序错 (开不了机) ★**网表 note 已落写法A (★ISS-283·12:30:23★) ⇒ 只剩板那一趟重画 land (★§③-2★)**★",
  "[实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 ⇒ 写法B ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通; ★**网表 note 已落写法A: pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) (★台账 §16.2 链头 L1353 · ISS-283 · 12:30:23★) ⇒ 板面与网表对不上**★",
  "板那一趟重画 Q_PG 的 3 根线 (★pad1→PWR_GOOD(G) / pad2→BAT_SW(S) / pad3→PWR_ON(D)★) + 网表 note 角色已于 2026-11-17 12:30:23 同批落成写法A (★S=BAT_SW / D=ON / G=PG★)",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])\" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON",
  "S6", "★**写法A 已拍 (★老板 2026-11-17 09:49★) + 网表 note 已落表 (★台账 §16.2 链头 L1353·12:30:23★) ⇒ 只剩板那一趟重画这 3 根线**★", "[实测]+[官网]"),
 ("B12_Q_ENVC_LAND", "ISS-241",
  "Q_ENVC 占位 land 序 (天然对上, 但必须核一遍)",
  "[实测] 板: pad1=PG_AND(G) / pad2=GND(S) / pad3=EN_VCORE(D) = G/S/D ⇒ 与 SOT-23 库序一致 (三件 MOS 里唯一天然对上的)",
  "核一遍 pad↔pin; 若落 AO3400A 则不用改 ⇒ 但不许跳过核 (换料就翻)",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_ENVC'][0].Pads()])\" ⇒ pad1=PG_AND / pad2=GND / pad3=EN_VCORE",
  "S6", "-", "[实测]"),
 ("B13_ESD_CAM_PAD", "ISS-244",
  "D_ESD_CAM 的 pad 序与单向件相反 (ESD 不工作 + CSI 负摆幅被钳到地)",
  "[实测] 板: pad1=GND / pad2=CSI_D0_CK_P; TPD1E05U06DPYR pin1=I/O / pin2=GND ⇒ 正好相反 (另两件 ESD 是 pad1=信号/pad2=GND)",
  "两个 pad 对调 ⇒ pad1=CSI_D0_CK_P(I/O) / pad2=GND",
  "bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='D_ESD_CAM'][0].Pads()])\" ⇒ pad1 挂 CSI_D0_CK_P",
  "S6", "-", "[实测]+[官网]"),
 ("B14_S6_20_COORDS", "ISS-274",
  "S6 的 20 个坐标固化钉位 (原文「21 个」是重复计数)",
  "[实测] 20 个 distinct 坐标 (10×R_SEL_* + 10×TP_DSI_*); 其中 19 个现值已等于目标 (固化钉位), 真实位移只有 R_SEL_D3_P 一处 (78.90, 9.50 → 122.30, 5.50)",
  "显式钉 20 个 (不是 21 个) ⇒ 写进 PCB_PART_POS 串",
  "python3 HW/check_board_frame_caliber.py ⇒ rc=0 (帧 id B160x100 · 20 个坐标逐个一致 ±0.01 mm)",
  "S6", "-", "[实测]"),
 ("B15_SVC_PORT_SPLIT", "ISS-276",
  "检修口/调试口开口必须拆成两个独立窗口 (合并不可行)",
  "[实测] 合并窗口跨 J_UART 罩 X 17.620..20.160 与 J_DEBUG 罩 X 142.063..143.838 ⇒ 并集宽 126.218 mm 装不下; 座体真实高度 [0数据]",
  "拆调试口罩 (J_DEBUG) 与 UART 罩 (J_UART) 两个窗口, 坐标按现役帧 B160x100 (★不得用 ISS-271 的 F30A 帧数 ★)",
  "python3 MECH/board_port_opening_s6_check.py ⇒ rc=0 (★属 MECH 域, 本单只登记不跑改 ★)",
  "S6", "P7 (老板) + MECH 侧 [0数据] 座体高度", "[实测]+[0数据]"),
 ("B16_LED_G_OPTO", "ISS-276",
  "D_LED_G 落位与 R_LED_G 分居板两端 (LED_G_D 走线 93.49 mm 横跨全板)",
  "[实测] 排版器按「功能排」落位 ⇒ D_LED_G 进 Y=56.80 的 LED 行 · R_LED_G 进 X=5.90 的 I2C 上拉列 ⇒ LED_G_D 走线 93.49 mm; 光孔 [0数据]",
  "归一到现役帧的 LED 落位带 (ISS-276 §5 已给两个窗口, 压 SoM 焊盘全 = 0)",
  "python3 MECH/board_port_opening_s6_check.py ⇒ rc=0",
  "S6", "MECH [0数据] 光孔 + P7", "[实测]+[0数据]"),
 ("B17_DNP_43", "ISS-269",
  "43 颗 DNP 位号在板上零标记 (R3 的 F3)",
  "[实测] R3-A4: MAIN_PCB且DNP «R3_T» 颗 · 在板上 «R3_O» 颗 · 零标记 «R3_Z» 颗 (★«R3_NOTE»)",
  "生成器侧 X-4 已修 (ISS-269) ⇒ 重出板自动打 exclude_from_bom / exclude_from_pos_files / dnp 三件套",
  "python3 HW/check_netlist_contradiction_r3.py ⇒ R3-A4 零标记 = 0 颗 (⇒ findings 只剩 F2)",
  "S7", "-", "[实测]"),
 ("B18_J_CHG_DISAMB", "ISS-247",
  "J_CHG 位号双义 + 板侧封装块不可装配 (R3 的 F2)",
  "[实测] R3-A3 命中 1 ⇒ F2 在; 板上 J_CHG 是 2 脚封装, 而实物是框侧座 + 脚侧座一对 (位号双义)",
  "位号消歧 (J_CHG_A / J_CHG_B) ⇒ 落表批次 + 板侧重出",
  "python3 HW/check_netlist_contradiction_r3.py ⇒ findings 只剩 F3 (随 B17 一起转绿)",
  "S7", "落表批次", "[实测]"),
 ("B19_BAT_DET", "ISS-266",
  "R_BAT_DET_1/2 的封装与阻值 (B-8, 条件步)",
  "[实测] 现值 1M ±1% @ (102.9, 17.5) / (107.7, 17.5); 分压链未落表 (V-3 归老板 A1)",
  "阻值 1M±1% → 100k / 60k 且封装随之改 ⇒ 只在 A1 拍板后才动",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R8 消失 (现状: R8 在)",
  "S5", "落表批次 (阻值归老板 A1)", "[实测]"),
 ("B20_LAND_8ROWS", "ISS-244",
  "8 行落表残项的 land 必须同批重画",
  "[实测] 落表残项 8 行: D_CHG_LED / D_LED_G / D_LED_R / SW_BOOT / SW_KEY_PWR / SW_KEY_VM / SW_KEY_VP / SW_RST ⇒ 其中 4 键 + 2 LED 的 land 必须同批重画",
  "落表批次落这 8 行 ⇒ 同批重画 land (★不许先改板后落表 ★)",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不增 (现状 18 条)",
  "S10", "落表批次", "[实测]"),
 ("B21_C_REGN_4U7", "ISS-241",
  "C_REGN 判据错: BOM 写 1µF, TI 手册 pin22 要求 4.7µF / 10V",
  "[实测] BOM value = 1µF; TI BQ25896 pin22 REGN 明写 Connect a 4.7 uF (10 V rating) ceramic capacitor",
  "落表批次改 BOM value ⇒ 板侧位置必须贴 U_CHG pin22",
  "python3 HW/check_part_selection_matrix.py ⇒ rc=0 (8/8)",
  "S10", "落表批次", "[官网]+[实测]"),
 ("B22_CHG_BOARD_FP", "ISS-241",
  "6 件充电板器件的 footprint 待定 (不在本板, 但会顶到本板那一趟)",
  "[实测] D_ESD_TC / FB_VBUS / D_TVS_VBUS / Q_CHG_LED / D_CHG_LED / C_REGN 六件 footprint = 待定 (板文件里查无此位号)",
  "充电板那一趟定 footprint (C_REGN 位置必须贴 U_CHG pin22) ⇒ 本板不受影响, 但不许与本板那一趟抢同一批落表窗口",
  "python3 HW/check_step1_parts_spec.py ⇒ rc=0",
  "S10", "充电板那一趟 (不在本板)", "[实测]"),
 ("B23_ESD_TC_4PAD", "ISS-244",
  "D_ESD_TC 落了 3 通道件却只接 1 通道 ⇒ Type-C 的 D+/D− 仍裸奔",
  "[实测] D_ESD_TC = SP0503BAHT (3 通道) 而网表只接 USB_VBUS_RAW + GND ⇒ 另 2 通道闲置",
  "充电板 footprint 给 4 焊盘 + 决定是否覆盖 D+/D−",
  "python3 HW/check_part_selection_matrix.py ⇒ rc=0",
  "S10", "老板 (ESD 架构: 单通道 vs 双通道)", "[实测]"),
 ("B24_Q_PG_PART", "ISS-241",
  "Q_PG 选漏电档还是栅压耐压档 (影响落料, 不影响 land 目标)",
  "[实测] 候选 DMP3098L (IDSS ≤800 nA, VGS 绝对最大手册未见 [0数据]) vs AO3407A (VGS ±20 V 明写, 高温 IDSS ≤5 µA 差 6 倍)",
  "一票交 main/PM; 两颗引脚序都是 1=G / 2=S / 3=D ⇒ 与 B11 的 land 目标一致, 不因选型变化",
  "python3 HW/check_part_selection_matrix.py ⇒ rc=0",
  "S10", "main/PM (ISS-241 Q-C)", "[官网]+[0数据]"),
 ("B25_UNCONNECTED", "ISS-266",
  "unconnected 归零 (45 → 0)",
  "[实测] unconnected items = 45 · DRC 违规 = 0 (骨架阶段允许未布线)",
  "布线归零 (S8); 死因见 ISS-265 §6 (A1 / W-1 / W-2 / W-4 / D_LED_G 位置 / FSIN_OUT)",
  "python3 state/check_pcb_drc.py ⇒ unconnected items = 0 · DRC 违规 = 0",
  "S8", "W-1/W-2/W-4 + A1", "[实测]"),
 ("B26_BASELINE", "ISS-266",
  "换基线 (旧 md5 → 新 md5)",
  "[实测] 现行基线: 板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07…",
  "那一趟跑完后把五件新 md5 写进作业包 §5 基线表 (追加式, 老行不删)",
  "md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv ⇒ 与新基线逐条一致",
  "S9", "-", "[实测]"),
 ("B27_CHAINGATE", "ISS-266",
  "投产包准入闸 chain_gate 转绿",
  "[实测] chain_gate rc=1 (③ PCB 准入红「板与网表不等价」 + ⑤ 投产资料包红)",
  "S1~S10 全跑完后重跑 chain_gate ⇒ 五个环节全绿",
  "python3 state/chain_gate.py ⇒ rc=0",
  "S11", "S1~S10", "[实测]"),
 ("B28_RELEASE", "ISS-266",
  "留证链 + 盖章 + 发布闸",
  "[实测] Gerber 32 个齐 (C6 通过); 留证链与盖章闸属 S12",
  "重出 Gerber / 钻孔 / CPL / 装配 / 3D / D356 + 留证链 + 盖章 + 发布闸",
  "python3 state/check_pcb_drc.py ⇒ C6 生产文件齐 · rc=0",
  "S12", "S10", "[实测]"),
 ("B29_WRITEBACK", "ISS-266",
  "回写台账 + 决策页 + 分片",
  "[实测] 落表台账 / 决策页 / 分片 三处待回写 (★板级结论必须落决策页 ★)",
  "把新 md5 四字段写进落表台账 + 决策页记板级结论 + 分片登记",
  "python3 state/merge.py ⇒ rc=0 && python3 state/gate_check.py ⇒ rc=0 (Q1 18/18)",
  "S13", "S9~S12", "[实测]"),
 ("B30_LED_BRIGHTNESS", "ISS-271",
  "LED 亮度档 G-5 **已拍 = 20mA 档** (R_LED_R 68Ω / R_LED_G 55Ω) ★**已落表 (★ISS-283·12:30:23★) ⇒ 板那一趟只须重出 BOM (footprint 不变 ⇒ 不构成额外板改)**★",
  "[实测] G-5 已拍「选项 ② = 改 R 到 20 mA 档」⇒ 已落表: R_LED_R = 68Ω ±1% / R_LED_G = 55Ω ±1% ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · 亮度 ×14 ⇒ IEC 62471 分级要重算 (★已登记 need·不代拍★); ★旧 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 (★已被 20 mA 档取代★)★",
  "落表已完成 (★R 值写进 BOM ⇒ 台账 §16.2 链头 L1353★) ⇒ 板那一趟只须重出 BOM + 投产包 (★footprint 不变 ⇒ 不构成额外板改★) ⇒ 另: IEC 62471 分级重算登记给 main (★不代拍★)",
  "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (★20mA 档已落表; 板侧项归 §③-1~§③-3★)",
  "S6", "★**已拍 (★老板 2026-11-17 09:49·A5 = 20mA★) ⇒ 剩【IEC 62471 分级重算】登记给 main (★不代拍★)**★", "[实测]+[官网]"),
 ("B31_P7_TARGET", "ISS-266",
  "P7: 画哪一块板 (160×100 台架板 vs 产品板)",
  "[实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10); 产品板 = 60×30 套A (★另一坐标帧 F30A, 数不可混用 ★)",
  "只列选项与代价, 不代拍 (★C4 是唯一不需动板的选项 ★)",
  "python3 HW/check_board_frame_caliber.py ⇒ rc=0 (三条帧 id B160x100 / F30A / P60x15 互不混用)",
  "S6", "老板 (P7)", "[实测]"),
]

FIELDS = ("id", "source_iss", "title", "current_state", "action",
          "criterion", "step", "blocked_by", "evidence")

# ★★真源读数 ⇒ 占位符替换 (★铁律 ①·现状值一律不许写死★) ★★
ITEMS = [tuple(subst(x, TOKENS) if isinstance(x, str) else x for x in it) for it in ITEMS_RAW]
objs = [dict(zip(FIELDS, it)) for it in ITEMS]

# ★★追加式订正块 (★sidecar 搬运·★老字一字不改·★缺 sidecar ⇒ fail-closed 拒写★) ★★
S3_BLOCK, ISS289_BLOCK, _BASELINE = read_appendix_blocks()

# ★★表格行的原样保留 (★ISS-283 手工订正的痕迹: 这 3 行的表格文字与 JSON 字段的 ★ 排版位置不同★)
# ★★⇒ 表格行按盘上原样保留 (★老字一字未删★), JSON 块按字段生成 ★★
TABLE_ROW_OVERRIDES = {
 "B32_V2_NET_RENAME": "| ★**`B32_V2_NET_RENAME`** ★ | ★ISS-283 ★ | V-2 网改名 (D_ESD_USB_D pad1: `USB_D_P_SRC` → `NET_USB_D_P_TYPEC`) ⇒ 板面 3 处焊盘网名必须同趟改 (★§③-1★) | ★**S4** ★ | ★**板只改一次那一趟 (★本单零写板★)** ★ | [实测] 网表 L417 已落 `NET_USB_D_P_TYPEC` (★台账 §16.2 链头 L1353 · ISS-283 · 12:16:08★); 板面仍挂旧网名 `USB_D_P_SRC` 的焊盘 **3 处**: `D_ESD_USB_D.pad1` / `R_SER_USB_D_P` 一端 / `J_SOM_P1` 的 USB_D_P 脚 ⇒ 网表与板对不上 | `python3 HW/check_board_frame_caliber.py` ⇒ C6 绿 (★盘上 md5 == 落表台账登记★) |",
 "B11_Q_PG_LAND": "| ★**`B11_Q_PG_LAND`** ★ | ★ISS-244 ★ | Q_PG 占位 land 序错 (开不了机) ★**★网表 note 已落写法A (★ISS-283·12:30:23★) ⇒ 只剩板那一趟重画 land (§③-2)★** ★ | ★**S6** ★ | ★**写法A 已拍 (★老板 2026-11-17 09:49★) + 网表 note 已落表 (★台账 §16.2 链头 L1353·12:30:23★) ⇒ 只剩板那一趟重画这 3 根线** ★ | [实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 ⇒ 写法B ⇒ Vgs=0 不导通, PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通; ★**网表 note 已落写法A: pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) ⇒ 板面与网表对不上** ★ | `bash state/pcbnew_py.sh -c \"import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])\" ⇒ pad1 挂 PWR_GOOD / pad3 挂 PWR_ON` |",
 "B30_LED_BRIGHTNESS": "| ★**`B30_LED_BRIGHTNESS`** ★ | ★ISS-271 ★ | LED 亮度档 G-5 **已拍 = 20mA 档** (R_LED_R 68Ω / R_LED_G 55Ω) ★**★已落表 (★ISS-283·12:30:23★) ⇒ 板那一趟只须重出 BOM (footprint 不变 ⇒ 不构成额外板改)★** ★ | ★**S6** ★ | ★**已拍 (★老板 2026-11-17 09:49·A5 = 20mA★) ⇒ 剩【IEC 62471 分级重算】登记给 main (★不代拍★)** ★ | [实测] G-5 已拍「选项 ② = 改 R 到 20 mA 档」⇒ 已落表: R_LED_R = 68Ω ±1% / R_LED_G = 55Ω ±1% ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · 亮度 ×14 ⇒ IEC 62471 分级要重算 (★已登记 need·不代拍★); ★旧 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 (★已被 20 mA 档取代★) ★ | `python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 (★20mA 档已落表; 板侧项归 §③-1~§③-3★)` |",
}
TABLE_ROW_OVERRIDES = {k: subst(v, TOKENS) for k, v in TABLE_ROW_OVERRIDES.items()}

STEPS = ["S%d" % i for i in range(1, 14)]
dist = {s: 0 for s in STEPS}
for o in objs:
    dist[o["step"]] = dist.get(o["step"], 0) + 1

# ★P4 覆盖度标记 (★从 6 份来源交卷单反查出来的板侧项标记 ★)
MARKERS = ["D_ESD_CAM", "Q_AND", "Q_PG", "D_ESD_TC", "U_LDO_S28", "J_CHG",
           "D_CHG_LED", "D_LED_G", "D_LED_R", "SW_BOOT", "SW_KEY_PWR",
           "SW_KEY_VM", "SW_KEY_VP", "SW_RST", "R_SEL_D3_P", "J_DEBUG",
           "J_UART", "R_SUPV_DIV", "U_SUPV", "TPS7A20", "Q_ENVC",
           "D_ESD_USB_D", "C_REGN", "C_VBUS_GND", "U_EN_SW", "R_BAT_DET_1"]

SOURCES = ["ISS-239", "ISS-241", "ISS-244", "ISS-247", "ISS-266",
           "ISS-269", "ISS-271", "ISS-274", "ISS-276"]

blob = json.dumps(objs, ensure_ascii=False)

L = []
A = L.append
A("# HW/PCB/BOARD_ONEPASS_PREFLIGHT.md · 「板只改一次」那一趟的【板侧项全集】")
A("")
A("> ★**派活**: `state/dispatch_briefs/ISS-277_hw_onepass_preflight_coverage.md` (项目总工 2026-11-17 07:3x) ★")
A("> ★**本单性质**: ★**内部活 · 纯分析 + 作业包订正 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★")
A("> ★**机器闸**: `python3 HW/check_onepass_preflight_coverage.py` (★P1~P6 + `--selftest` ★) ★")
A("> ★**配套作业包**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (§3-S0 = 本清单的并入摘要) ★")
A("")
A("★**一句话口径**: ★**这一页是「板只改一次」那一趟 (S1~S13) 的板侧项全集** ⇒ ★**任何一项只在交卷单里、没进这一页 = 当场红** ★")
A("★**为什么必须有这一页**: ★**板侧项现在散在 ≥6 份交卷单 + 2 个闸 + 1 份作业包里, 没有任何一处是全集** ⇒ ★**漏做一项 = 板 md5 变第二次 = 留证链 / Gerber / 投产包 / 盖章全白跑一遍** ★")
A("")
A("---")
A("")
A("## §1 · 坐标帧声明 (★三条帧互不混用 ★)")
A("")
A("| 帧 id | 含义 | 本页用在哪 |")
A("|---|---|---|")
A("| ★**`B160x100`** ★ | ★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★ | ★**本页所有坐标与判据一律用它** ★ |")
A("| `F30A` | 60×30 套A 帧 | ★**只作对照, 不可代入** ★ |")
A("| `P60x15` | 60×15 帧 | ★**只作对照, 不可代入** ★ |")
A("")
A("★**权威帧表** = `HW/PCB/BOARD_FRAME_CALIBER.md` §6 (ISS-274) · ★**机器闸** = `python3 HW/check_board_frame_caliber.py` ★")
A("")
A("---")
A("")
A("## §2 · 逐条表 (★每条固定 9 个字段 ★)")
A("")
A("★**字段**: `id` / `source_iss` / `title` / `current_state` (★必带证据等级 ★) / `action` / `criterion` (★真命令 + 期望 rc/期望值 ★) / `step` (★∈ S1~S13 ★) / `blocked_by` / `evidence` ★")
A("")
A("| id | source_iss | title | step | blocked_by | current_state (★实测值 ★) | criterion (★真命令 ★) |")
A("|---|---|---|---|---|---|---|")
for o in objs:
    ov = TABLE_ROW_OVERRIDES.get(o["id"])
    if ov:
        A(ov)
        continue
    A("| ★**`%s`** ★ | ★%s ★ | %s | ★**%s** ★ | %s | %s | `%s` |" % (
        o["id"], o["source_iss"], o["title"], o["step"], o["blocked_by"],
        o["current_state"], o["criterion"]))
A("")
A("---")
A("")
A("## §3 · 新发现并入表 (★6 个来源单逐条映射 ★)")
A("")
A("| 来源单 | 板侧发现 | 本页对应条目 | 状态 |")
A("|---|---|---|---|")
A("| ★**ISS-241** (sw-lead 11-16 22:2x) ★ | ★F-1 `D_ESD_CAM` 器件脚接反 · F-2 `Q_AND` pad 序 D/S/G vs 库 G/S/D · `D_ESD_TC` 3 通道件 ⇒ 充电板 footprint 得给 4 焊盘 · `C_REGN` 判据错 (1µF→4.7µF) · `Q_PG` 漏电档 vs 栅压耐压档 ★ | ★`B13_ESD_CAM_PAD` / `B10_Q_AND_LAND` / `B12_Q_ENVC_LAND` / `B23_ESD_TC_4PAD` / `B21_C_REGN_4U7` / `B24_Q_PG_PART` ★ | ★**作业包缺 → 本页补入** ★ |")
A("| ★**ISS-244** (sw-lead 11-17 00:0x) ★ | ★三条实物级 P0: `Q_PG` 角色错 (开不了机) · `Q_AND` 栅漏对调 · `D_ESD_CAM` 接反 · 另: `R_SUPV_DIV1/2` 0Ω×必装 + `U_SUPV` DNP ⇒ 装 0Ω 短地 · 8 行落表残项 ★ | ★`B11_Q_PG_LAND` / `B10_Q_AND_LAND` / `B13_ESD_CAM_PAD` / `B04_R_SUPV_DIV_DNP` / `B20_LAND_8ROWS` ★ | ★**作业包缺 → 本页补入** ★ |")
A("| ★**ISS-247** (hw-lead 11-17 00:2x) ★ | ★F2 `J_CHG` 位号消歧 · F3 板侧 43 颗 DNP 零标记 ★ | ★`B18_J_CHG_DISAMB` / `B17_DNP_43` ★ | ★F3 ≈ §3-S7 (★**只核对** ★) · ★F2 **作业包缺 → 本页补入** ★ |")
A("| ★**ISS-274** (hw-lead 11-17 06:5x) ★ | ★S6 真实位移只有 `R_SEL_D3_P` 一处 (20 distinct 不是 21) · 坐标帧声明 ★ | ★`B14_S6_20_COORDS` / §1 坐标帧声明 ★ | ★**已并入 (追加式) → 本页只核对** ★ |")
A("| ★**ISS-276** (mech-lead 11-17 07:0x) ★ | ★检修口/调试口开口**必须拆成两条** (合并不可行) · 座体真实高度 **[0数据]** · `D_LED_G` 光孔 **[0数据]** ★ | ★`B15_SVC_PORT_SPLIT` / `B16_LED_G_OPTO` ★ | ★**作业包缺 → 本页补入** ★ |")
A("| ★**ISS-239** (hw-lead 11-16 2x) ★ | ★`U_LDO_S28.pin3` A/B 两案 ⇒ **若走 A 案, 板必须补 pad3** · 7 颗 TPS7A20 板封装 Value = 脚功能串 ★ | ★`B03_ULDO_S28_PAD3` / `B06_TPS7A20_VALUE` ★ | ★**作业包缺 → 本页补入** ★ |")
A("| ★**ISS-269 / ISS-266 / ISS-271** (本轮窗口内) ★ | ★X-3/X-4/B-2 三坑 (生成器侧已修) · S1~S13 作业包本体 · LED 亮度档 G-5 未拍 ★ | ★`B05_U_EN_SW_VALUE` / `B17_DNP_43` / `B01`~`B31` 全表 / `B30_LED_BRIGHTNESS` ★ | ★**作业包已有 (只核对) + 生成器侧已修** ★ |")
A("| ★**ISS-283** (hw-lead 2026-11-17 12:16~12:30 真落表后) ★ | ★**V-2 网改名 (A3) + W-4 写法A (A4) + G-5 20mA 档 (A5) 三次落表 ⇒ 板那一趟必须同趟吃掉 3 条板侧同步项 (★见下面 §3-追加 三条★)** ★ | ★`B32_V2_NET_RENAME` (§③-1) · `B11_Q_PG_LAND` (§③-2) · `B07_ESD_USB_D_3PIN` / `B08_ESD_USB_D_NEAR` / `B09_ESD_USB_D_MINUS` (§③-3) · `B30_LED_BRIGHTNESS` (G-5 已落) ★ | ★**本页补入 (追加式) · 板那一趟清掉** ★ |")
A("")
# ★★ISS-283 的 §3-追加 块 (★sidecar 搬运·★老字一字不改★) ★★
for l in S3_BLOCK:
    A(l)
A("")
A("---")
A("")
A("## §4 · 归属步分布表 (★S1~S13 每步至少一条, 不许有步没人管 ★)")
A("")
A("| 步 | 条数 | 条目 |")
A("|---|---|---|")
for s in STEPS:
    ids = [o["id"] for o in objs if o["step"] == s]
    A("| ★**%s** ★ | ★%d ★ | ★%s ★ |" % (s, dist.get(s, 0), ", ".join("`%s`" % i for i in ids) or "—"))
A("")
A("---")
A("")
A("## §5 · 归老板 / 归 main 拍的清单 (★只列, 不代拍 ★)")
A("")
A("| # | 事项 | 为什么要先拍 | 谁拍 | 拍了之后板侧要做什么 |")
A("|---|---|---|---|---|")
A("| ★1 ★ | ★**`U_LDO_S28.pin3` A/B 案** ★ | ★**A 案 ⇒ 板必须补 pad3** ⇒ 拍晚了 = 板要改第二次 ★ | ★老板/PM (ISS-239 §4.2) ★ | ★`B03` ⇒ 补 pad3 + 脚表补行 ★ |")
A("| ★2 ★ | ★**LED 亮度档 G-5** ★ | ★**亮度档一改 ⇒ 改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位** ⇒ 排在 S6 之后 = 板改第二次 ★ | ★老板 (ISS-271) ★ | ★`B30` ⇒ 串阻落表 + 板面落位 ★ |")
A("| ★3 ★ | ★**P7 画哪一块** (160×100 台架板 vs 产品板 60×30) ★ | ★**C4 是唯一不需动板的选项** ⇒ 不拍就动板 = 白改 ★ | ★老板 (ISS-266 §7) ★ | ★`B31` + 全部坐标帧声明 ★ |")
A("| ★4 ★ | ★**`D_ESD_TC` 4 焊盘 footprint 方案** ★ | ★3 通道件只接 1 通道 ⇒ Type-C D+/D− 仍裸奔 ⇒ 架构题 ★ | ★老板 (ESD 单通道 vs 双通道) ★ | ★`B23` ⇒ 充电板那一趟 ★ |")
A("| ★5 ★ | ★**ESD 架构 (W-1/W-2)**: 一颗双通道 vs 两颗单通道 ★ | ★`D_ESD_USB_D` 换 3 脚 = 双通道架构 ⇒ **不拍就动板 = 白改** ★ | ★老板 ★ | ★`B07`/`B08`/`B09` (★S4 是第一个真正卡在老板的步 ★) ★ |")
A("| ★6 ★ | ★**`Q_PG` 写法A (S=BAT_SW / D=ON / G=PG)** + **漏电档 vs 栅压耐压档** ★ | ★**写法B = 开机路径彻底不通** ⇒ land 按错角色排 = 白投一版 ★ | ★PM/老板 + main ★ | ★`B11` / `B24` ★ |")
A("| ★7 ★ | ★**A1 (V-3) 分压最终阻值** ⇒ `R_SUPV_DIV1/2` 与 `R_BAT_DET_1/2` ★ | ★**阻值一改 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位** ⇒ 排在那一趟之后 = 板改第二次 ★ | ★老板 (A1) ★ | ★`B04` / `B19` ★ |")
A("")
A("---")
A("")
A("## §6 · 覆盖度标记表 (★P4 的判据来源: 从 6 份来源交卷单反查 ★)")
A("")
A("★**每个标记都必须在下面 §7 的 JSON 里出现** ⇒ ★**漏一条即红** ★")
A("")
A("```text")
A("标记清单 (%d 个):" % len(MARKERS))
A("\n".join(MARKERS))
A("```")
A("")
A("★**来源单全集 (★清单里每条 `source_iss` 必须落在这个集合里 ⇒ 不许有来源不明的项 ★)** ★")
A("")
A("```text")
A("\n".join(SOURCES))
A("```")
A("")
A("---")
A("")
A("## §7 · 机器可读 JSON 块 (★★闸读它 · ★★本块放最后 ★★)")
A("")
A("★**格式**: `schema` = `board-onepass-preflight/v1` · `frame` = `B160x100` · `items[]` 每条固定 9 个字段 ★")
A("★**★不许改格式**: 闸 `HW/check_onepass_preflight_coverage.py` 按这 9 个字段判 (★缺一个即红 ★) ★")
A("")
A("```json")
A(json.dumps({"schema": "board-onepass-preflight/v1", "frame": "B160x100",
              "items": objs}, ensure_ascii=False, indent=2))
A("```")
A("")
A("---")
A("")
A("★**★本表的每个数字都是本机实读 (★`bash state/pcbnew_py.sh` 读板 / 各闸原始输出 / 来源交卷单原文 ★), 没有一条是估的★★** ★")
A("★**★本页由 `state/_iss277_build_preflight.py` 生成 (★页与 JSON 同源 ⇒ 不会写岔 ★)★** ★")
A("")
A("---")
A("")
# ★★ISS-289 的 §附录 块 (★sidecar 搬运·★老字一字不改·★含 state_baseline 登记表★) ★★
for l in ISS289_BLOCK:
    A(l)

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("★已写 %s (%d 条, %d 字节)" % (OUT, len(objs), os.path.getsize(OUT)))
print("★步分布:", dist)
print("★缺覆盖的步:", [s for s in STEPS if dist.get(s, 0) == 0])
