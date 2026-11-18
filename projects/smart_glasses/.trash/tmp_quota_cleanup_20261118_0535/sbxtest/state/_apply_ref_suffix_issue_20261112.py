#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_ref_suffix_issue_20261112.py —— ★★开单 ISS-205: 位号加数字后缀 (★问号真根因已钉死★)★★

★★为什么开这一单 (★main 2026-11-12 03:0x 实测坐实★)★★:
  ★**B 项「位号改名」卡了整链重出两天, 根因一直记成「下划线命名」⇒ ★**实测证明那是错的**⇒
  ★**真根因 = 【KiCad 判定「已标注」的条件是位号末字符为数字】** ⇒ ★**解法 = 加 `_1` 后缀 (★不是去下划线★)**

★★★本单必须做的事 (★★)★★★
  ① ★**改在产生点**: `state/gen_kicad_sch.py` 的符号生成处 ⇒ 给位号加数字后缀
     (★三处同步: `(property "Reference")` / `(instances … (reference))` / `lib_symbols` 的 `SYM_*` 名★)
  ② ★**★不许手改产物** (★`HW/PCB/demo_mainboard*.kicad_sch` 是产物 ⇒ 重跑会冲掉★)
  ③ ★**顺带补**: 10 个子页缺 `(sheet_instances (path "/<根页uuid>" (page "N")))` ⇒ 层级工程结构缺件
  ④ ★**不动板 / 不动网表** (★B 项的板侧改动属整链重出第 1 步, 不在本单★)

★★判据 (★可机械验★)★★:
  ★**① `bash state/kicad.sh sch export bom -o /tmp/x.csv --fields Reference HW/PCB/demo_mainboard.kicad_sch`
      ⇒ 输出里带 `?` 的行数 = 0** (★当前实测 186★)
  ★**② 导出时 stderr 【不许出现】"schematic has annotation errors"** (★当前实测出现★)
  ★**③ `python3 state/check_sch_erc.py` rc=0** · ★**`check_sch_pinfull.py` rc=0 (K=0)** · ★**`check_sch_loadable.py` rc=0**
  ★**④ 位号唯一性**: 218 个位号无重复 (★实测加 `_1` 后缀零撞名★)
  ★**⑤ 受保护文件 md5 全未变**: 板 `611b869e…` · 网表 `c78f9912…` · 脚表 `4814617e…` · `.kicad_pro` `3e504d2b…`
  ★**⑥ 板里 186 个封装位号 【本单不许动】** (★板侧改动属整链重出第 1 步★) ⇒ 原理图位号与板位号此刻【会不一致】⇒
      ★★这是【预期的中间态】⇒ ★★**必须在交卷报告里写明** ⇒ ★★且【不许因此去改板】★★

★**落账纪律 (★项目既有范式★)**: flock + 锁内重读 + 只新增一条 + 原子写 + yaml 往返自检 + 逐条 diff 实测
"""
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_iss205_20261112"
IID = "ISS-205"

NEW_ISSUE = {
    "id": IID,
    "title": "★★[主线内·原理图侧·内部活] ★★KiCad 导出 BOM 里 186 个位号带 `?` (★板厂看到的位号与丝印对不上★) "
             "⇒ ★★真根因已实测钉死 = 【KiCad 判「已标注」的条件是位号末字符为数字】⇒ ★★解法 = 给位号加 `_1` 数字后缀 "
             "(★★不是去掉下划线 —— 实测去下划线无效且会让位号不可读★★) ⇒ 改在生成器里★★",
    "severity": "high",
    "source_blocker": "SW-TIM-B1",
    "source_agent": "main",
    "desc": "★2026-11-12 03:0x 项目总工开单 (★依据 = `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md` 的实测证据链★)。\n"
             "★**现象 [实测]**: ★**KiCad 从原理图导出的 BOM (`HW/PCB/production/doc/demo_mainboard-kicad-bom.xml`) 里 "
             "218 个位号有 186 个带 `?` 后缀** ⇒ ★**板厂拿这份 BOM 去对丝印位号会对不上** ⇒ ★**而我们自己的 "
             "`HW/BOM_v1.csv` (0/218)、板文件 (0/186)、原理图子页 (0/218) 三处位号字符串都是干净的** ⇒ "
             "⇒ ★**真问题不是「位号字符串对不上」, 是【KiCad 导出的那份多了个 `?`】** ★★\n"
             "★**★真根因 [实测·零例外]★**: ★**KiCad 判定一个符号「已标注 (annotated)」的条件 = 【它的位号最后一个字符是数字】** ⇒ "
             "★**位号末字符是字母 ⇒ 判未标注 ⇒ 导出 BOM 时打 `?`** ⇒ ★**实测: 带 `?` 的 186 个末字符 100% 是字母; "
             "不带 `?` 的 32 个末字符 100% 是数字 (零例外)** ⇒ ★**并在 /tmp 造了最小对照工程逐个换位号复现 (★如 "
             "`C_KEY_CAM_A1` 不带? 而 `C_KEY_CAM_1A` 带? ⇒ 【是最后一个字符, 不是最后一段】★)** ⇒ "
             "⇒ ★**★★旧记录说的「根因是下划线命名」是错的 ⇒ 已订正★★** ★★\n"
             "★**★解法 [实测·已在副本上跑通]★**: ★**给 186 个位号统一加 `_1` 数字后缀 (★32 个本来就数字结尾的不动★)** ⇒ "
             "★**实测: 改完导出 BOM, 带 `?` 行数 = 0, 且 KiCad 的 \"schematic has annotation errors\" 警告一并消失** ⇒ "
             "★**且实测【零撞名】(186 个 ref 加 `_1` 后与现有 218 个位号无冲突)** ⇒ "
             "⇒ ★**★★这个方案比原设想的「去掉下划线」好得多 (★去下划线实测【无效】+ 会把 `C_AC_CSI_D0_CK_N` 变成 "
             "`CACSICSID0CKN` 这种不可读的东西; 加后缀可读性只多一个尾巴, 且不用设计命名规则★)⇒ ★★B 项实现方案据此改写★★** ★★\n"
             "★**★必须三处同步改 (★我实验时只改一处就被 KiCad 报 annotation errors★)★★**: "
             "① 子页 `(property \"Reference\" \"X\" …)` ② 子页 `(instances … (reference \"X\") (unit 1))` "
             "③ `lib_symbols` 里的 `(symbol \"SYM_X\" …)` + 两个子符号 `SYM_X_0_1` / `SYM_X_1_1` ⇒ "
             "⇒ ★**落点 = `state/gen_kicad_sch.py` 的符号生成处 (★改在产生点★)** ⇒ ⇒ ★**★不许手改 "
             "`HW/PCB/demo_mainboard*.kicad_sch` (★那是产物, 重跑就冲掉★)★★** ★★\n"
             "★**顺带修的结构缺件**: ★**实测我们的 10 个子页都缺 `(sheet_instances (path \"/<根页uuid>\" (page \"N\")))`** "
             "⇒ 根页有 `(sheet_instances (path \"/\" (page \"1\")))` 而子页一个都没有 ⇒ ★**KiCad 官方模板的子页是有的** ⇒ "
             "⇒ ★**这是我们自己生成器造出来的层级工程结构缺件 (★与问号不是同一个因: 补上后问号数没变, 但它本来就该有★)** ⇒ "
             "⇒ ★**随本单一趟补 (★也在生成器里加★)** ★★\n"
             "★**★★注意: 本单会让【原理图位号】与【板上位号】暂时不一致 (★186 个封装位号不动★) ⇒ "
             "★这是【预期的中间态】(★板侧改动属整链重出第 1 步, 与 C/D/E 合并落表★) ⇒ ★★**不许因此去改板**★★**",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": "2026-11-12",
    "due": "2026-11-14",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "task_brief": (
        "★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: ★**在 `state/gen_kicad_sch.py` 里给位号加 `_1` 数字后缀** "
        "⇒ ★**让 KiCad 导出的 BOM 不再带 `?`** ⇒ ★**★只改原理图生成器, 不碰板/网表/BOM台账★★**\n\n"
        "★**★① 根因 (★main 已实测坐实·你不用重查·零例外★)★**:\n"
        "  · ★**KiCad 判「已标注」的条件 = 【位号最后一个字符是数字】** ⇒ ★**末字符是字母 ⇒ 判未标注 ⇒ BOM 里打 `?`**\n"
        "  · ★**实测: 带 `?` 的 186 个位号末字符 100% 是字母; 不带 `?` 的 32 个末字符 100% 是数字**\n"
        "  · ★**★旧记录说的「根因是下划线命名」是错的 ⇒ 不要去动下划线★★**\n"
        "  · ★**★解法: 加 `_1` 后缀 (★已在本机副本上跑通: 问号行数 0 + annotation errors 警告消失 + 零撞名★★)**\n"
        "  · ★**完整证据: `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md` (★建议先读这一份, 里面有全部对照实验★)**\n\n"
        "★**★② 要改哪三处 (★必须同步, 少改一处 KiCad 就报 annotation errors★)★**:\n"
        "  1. ★**子页的 `(property \"Reference\" \"X\" …)`** ⇒ `X` → `X_1`\n"
        "  2. ★**子页的 `(instances … (reference \"X\") (unit 1))`** ⇒ `X` → `X_1` (★KiCad 导出 BOM 实际读这里★)\n"
        "  3. ★**`lib_symbols` 里的 `(symbol \"SYM_X\" …)` + 两个子符号 `SYM_X_0_1` / `SYM_X_1_1`** ⇒ 同步改\n"
        "  ⇒ ★**落点 = `state/gen_kicad_sch.py` 的符号生成处 (★★改在产生点★★) ⇒ ★★不许手改 "
        "`HW/PCB/demo_mainboard*.kicad_sch` (★那是产物, 重跑就被冲掉★)★★**\n\n"
        "★**★③ 顺带补 (★同一趟做完★)★**: ★**10 个子页都缺 `(sheet_instances (path \"/<根页uuid>\" (page \"N\")))`** ⇒ "
        "★**根页有 `(sheet_instances (path \"/\" (page \"1\")))` 而子页一个都没有 ⇒ KiCad 官方模板的子页是有的** ⇒ "
        "⇒ ★**在生成器里给每个子页补上 (★page 号 = 根页里那个 sheet 的 `(instances … (path \"/<root>\" (page \"N\")))` 的 N★)**\n\n"
        "★**★④ 判据 (★六条, 缺一条不算交卷★)★★**:\n"
        "  ① ★**`bash state/kicad.sh sch export bom -o /tmp/x.csv --fields Reference HW/PCB/demo_mainboard.kicad_sch` "
        "⇒ 输出里带 `?` 的行数 = 0** (★当前实测 **186**★)\n"
        "  ② ★**导出时 stderr 【不许出现】`schematic has annotation errors`** (★当前实测出现★)\n"
        "  ③ ★**`python3 state/check_sch_erc.py` rc=0** · ★**`python3 state/check_sch_pinfull.py` rc=0 (★K=0★)** · "
        "★**`python3 state/check_sch_loadable.py` rc=0**\n"
        "  ④ ★**位号唯一性: 218 个位号无重复** (★实测加 `_1` 后缀零撞名, 你落完再核一遍★)\n"
        "  ⑤ ★**受保护文件 md5 全未变**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · "
        "脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`\n"
        "  ⑥ ★**板里 186 个封装位号 【本单不许动】** ⇒ 原理图位号与板位号此刻【会不一致】⇒ "
        "★**这是【预期的中间态】** (★板侧改动属整链重出第 1 步★) ⇒ ★★**不许因此去改板★★**\n\n"
        "★**★★⑤ 交卷 (★≤8 行·别写长篇★)**: ① 问号行数 (前→后) ② annotation errors 警告 (前→后) "
        "③ 三条闸 rc ④ 位号唯一性实测 ⑤ 板/网表/脚表/.kicad_pro md5 未变的实测 "
        "⑥ 改了哪个文件 + 【原理图与板位号暂时不一致】的说明 ★★\n\n"
        "★**★★⑥ 边界 (★再强调一次★)**: ★**不许碰**: `HW/PCB/demo_mainboard.kicad_pcb` · `HW/netlist_v1.csv` · "
        "`HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/BOM_v1.csv` · `HW/PCB/FET3572C_PIN_TABLE.csv` · "
        "`state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · 别人的分片 ⇒ ★**只许写**: `state/gen_kicad_sch.py` · "
        "`HW/PCB/demo_mainboard*.kicad_sch` (★产物·由生成器重跑产生★) · `HW/PCB/PIN_REALITY_GAP.md` (★若生成器会重跑它★) · "
        "`HANDOFF/` 交卷报告 · ★**必要时** `state/fragments/hw.yaml` (走 `frag_write.py`·只许新增本单相关条目★)\n"
        "★**★不许发任何邮件 / 询价 / 问询 (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ "
        "所有资料一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ "
        "★**查不到就写 `[0数据]` + 已知缺口 + 降级方案 ⇒ 没有「批一句可以发」这个选项★★**"
    ),
    "dispatched_at": "",
    "fixed_at": "",
}


def dump_atomic(obj, path, width):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        items = doc if isinstance(doc, list) else doc.get("issues")
        width = None
        for w in (60, 80, 100, 120, 200):
            if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=w) == raw:
                width = w
                break
        print("★当前排版 width = %s" % (width or "探不到 (★用 200 + 逐条 diff 兜底★)"))
        width = width or 200
        if any(str(i.get("id")) == IID for i in items):
            print("ℹ️ %s 已存在 ⇒ 不动" % IID)
            return 0
        shutil.copy2(LOG, BAK)
        items.append(NEW_ISSUE)
        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(doc, LOG, width)
        print("✅ 已原子写 issue_log.yaml: 新增 %s (★备份 %s★)" % (IID, os.path.basename(BAK)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
