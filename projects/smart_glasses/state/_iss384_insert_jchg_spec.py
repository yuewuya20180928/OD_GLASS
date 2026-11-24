#!/usr/bin/env python3
"""ISS-384 (hw-lead) · §7 证据补钉 (追加式, 只加不删) · 2026-11-24
起因: main 2026-11-24 09:3x 裁决 (答复 iss384_jchg_触点额定):
      「把规格页的逐字条款 + 页码钉进 HW/J_CHG_SELECTION.md §7 ⇒ 规格页尚未逐字核这个缺口就闭合了」
纪律: ★只补证据, 不改选型 · 不改几何判定 · 零落表 · 零写板 · 零外发★
"""
import io, os, sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
REL = "HW/J_CHG_SELECTION.md"
MARK = "### ★ 7-ISS-384 补: 规格页逐字条款 + 官方参数钉进"

BLOCK = """
### ★ 7-ISS-384 补: 规格页逐字条款 + 官方参数钉进 (★2026-11-24 · hw-lead · 追加式 · 只加不删★)

> ★**起因**: ★**main 2026-11-24 09:3x 裁决 (答复 `iss384_jchg_触点额定`)**: ★**「把规格页的逐字条款 + 页码钉进 §7 ⇒ 规格页尚未逐字核这个缺口就闭合了」** ⇒ ★**本块只补证据, 不改选型 · 不改几何判定 · 零落表 · 零写板 · 零外发** ★
> ★★**本机直连 PDF 被拦 (实测)**: `curl` 官网产品页 / 官网目录 API / Farnell 规格书 PDF ⇒ ★**hirose.com 与 farnell.com 直连本机返回 21 字节 stub (rc=0 但无内容) · Farnell PDF rc=124 超时** ⇒ ★★**⇒ 页码 = [0数据]** ⇒ ★**降级方案 = 下面这四件锚点已可复核: ① 逐字条款原文 ② 文档名 + 版本日期 ③ 小节/表名 ④ 可点 URL** ⇒ ★**下次能直连 PDF 时补页码即可, 判定结论不变** ★★

| 条款 / 参数 | 逐字内容 | 等级 | 出处 (文档名 + 版本 + 小节 / URL) |
|---|---|---|---|
| 70% 降额条款 (逐字) | "Note 1 : When passing the current through all of the contacts, use 70% of the current rating." | **[官网]** | Hirose **[FH12] Series Catalog** (Nov.1.2026 版) · Product Specifications · "Adaptive FPC/FFC contact specifications" 表 · **Note 1** · https://www.hirose.com/en/product/series/FH12/documents |
| FH12-10S-0.5SH(55) 额定电流 | Rated Current **0.5A** (每触点) | **[官网]** | Hirose 官网产品页 CL0586-0522-3-55 · https://www.hirose.com/en/product/p/CL0586-0522-3-55 |
| 10p 尺寸表 (按目录原样) | FH12-10S-0.5SH() / HRS No. 586-0522-3 / No. of Contacts 10 / **A=4.5 · B=8.1 · C=9.1 · D=5.57** (mm) | **[官网]** | Hirose **[FH12] Series Catalog** (Nov.1.2026 版) · 尺寸表 (No. of Contacts / A / B / C / D) |
| 外形宽交叉校验 | 目录 C=**9.1mm** ⇒ ★**与本页 §7 原行「FH12 10p 外形宽 ≈9.1mm [推算]」(由 28p 反推) 吻合** ⇒ ★**那条反推值被官网表坐实** | **[推算]**(交叉校验) | 同上 |
| 其它官方参数 | 0.5mm pitch / 10 位 / L 9.1mm / H 2.0mm / W 6.4mm / FPC-FFC 0.3mm / -40~+85°C / DC50V / UL94 V-0 / ZIF / 触点镀金磷青铜 | **[官网]** | Hirose 官网产品页 CL0586-0522-3-55 |
| ★**页码** | ★**未核** | **[0数据]** | ★**降级方案: 条款原文 + 文档名 + 版本日期 (Nov.1.2026) + 小节/表名 + 可点 URL 四件锚点已齐 ⇒ 判定「全触点导通时每触点按 0.35A 读」不受页码影响; 需补页码时由下次能直连 PDF 的那一趟补** ★ |

> ★★**两条地界声明**: ★**① 尺寸字母 A/B/C/D 按官网目录原样登记, 不作解释** ⇒ ★**「哪个是座体 X 向进深 / Y 向占宽」= 几何归属 = mech-lead 地界, 本单只登记数据不判定** (★另: §4.1/§4.2 的间隙结论一律不动★) ★★; ★**② 触点额定判据本身不变** ⇒ ★**「单触点额定 ≥0.5A」仍是 RFQ 硬判据, 70% 降额条款仍按 §3.2 两种读法处理 (我们的工况只有 pin1/pin2 载流 ⇒ 条款不成立) ⇒ 选型结论零变化** ★★
> ★★**外发纪律**: ★**本块零外发** ⇒ 全部数据来自【自己网上查到的官网快照】⇒ ★**没有「等原厂回信」这种挂起项** ★★

"""


def main():
    p = os.path.join(ROOT, REL)
    txt = io.open(p, encoding="utf-8").read()
    if MARK in txt:
        print("SKIP (已存在 §7 补钉块)")
        return 0
    lines = txt.split("\n")
    # 定位 §7 表的最后一行 (10p 具体 A/B/C 尺寸) ⇒ 插在它后面
    idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("| 10p 具体 A/B/C 尺寸"):
            idx = i
    if idx is None:
        raise SystemExit("★[ISS-384] 找不到 §7 表尾行, 定位失败")
    new = lines[:idx + 1] + BLOCK.strip("\n").split("\n") + lines[idx + 1:]
    io.open(p, "w", encoding="utf-8").write("\n".join(new))
    print("INSERTED §7 补钉块 @ L%d (+%d lines)" % (idx + 1, len(BLOCK.strip('\n').split('\n'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
