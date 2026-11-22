#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261122_2125_main_sign_iss337_answer_3needs.py
======================================================
main (项目总工) 2026-11-22 21:2x 本机实跑 ⇒ 两件事:

① 【签收】ISS-337 cont2 交卷 ⇒ `fixing` → `verified`
   ★签收依据 = main 本机独立复核 (不抄 agent 报告) ★
   ★★签收前 main 自己抓到并修掉了一处假引用 (cont2 会话被 run timeout 掐死留下的洞) ★★

② 【裁 need】ISS-337 交回 main 的 3 条机制级 need ⇒ 写进 main 自己的分片 pm.yaml
   ★只写 main 自己的 pm.yaml (不碰 hw.yaml / sw.yaml / mech.yaml) ★

边界 (一条都不破):
  ★零写板   ★零落表 (网表/脚表/BOM 不动)   ★零改闸   ★零改真生成器
  ★零外发   ★不替老板拍板   ★不自签别人分片   ★零改动别人文档 (只动 ISS-337 交卷页的件数/补证行)
"""
import os
import shlex
import shutil
import subprocess
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
PMF = os.path.join(PROJ, "state/fragments/pm.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


# ---------------------------------------------------------------- ① 签收 ISS-337
VERIFY = (
    "✅ verified (★main 2026-11-22 21:1x~21:3x 本机独立复核·不抄 agent 报告★) "
    "⇒ 交卷物在盘: · 交卷页 `HANDOFF/2026-11-19_hw-lead_ISS337_段数追平根因定位.md` (41,022 B @2026-11-22 20:5x · "
    "★main 补证后 +件数行★) · 主交付物 `HW/PCB/ONETRIP_S8_SEGMENT_PARITY_ROOTCAUSE.md` (27,368 B @20:59) · "
    "证据 `logs/iss337/` ★**23 件**★ (★main 补齐第 16 件·详见下段★) · "
    "分片 `state/fragments/hw.yaml` (`grep -c iss337` = **14** · 零重复 key) ★ "
    "★**main 本机独立复跑 (21:1x)**★: ① `TMPDIR=$PWD/tmp python3 tmp/iss337/seg_parity_selfcheck.py --selftest` ⇒ "
    "末行 `ALL TESTS PASS` + `SELFTEST_RC=0` (★五块同工艺板全在带内: 官方终板 2649/433/5726.9 · 官方 stage-1 2537/408/5563.9 · "
    "现役 v76mg1 2582/471/5582.8 · v76mz 3099/486/5426.6 · iss325ctl 3129/505/5483.9 ⇒ 老口径会把官方板自己拦掉★) "
    "② `state/gate_check.py` ⇒ rc=0 · **Q1 = 18/18** · hw-lead **6/6 缺: 无** · Q7 9/9 · extra_gates 8/8 "
    "③ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
    "④ 交卷页 + 主交付物 占位符/假引用 grep = **0** ⑤ 页面引用的 17 个 `logs/iss337/*` 文件逐个在盘 ⇒ **0 MISS** "
    "★ **★★main 补证 1 件 (★cont2 会话被 run timeout 掐死留下的洞·★签收前自己抓到的★)★★★**: "
    "cont2 子会话 (`8ee142bb` / `a04354d4`) 于 **21:08:44 status=timeout 掐死** (★它自己在 **21:07:17** 的自检里已自报 "
    "`MISS logs/iss337/16_official_s1_drc.txt`·但没来得及修★) ⇒ ★交卷页 §B1 第 8 行引用一个**不存在的文件** = 假引用 ⇒ "
    "G4 不通过 ⇒ **main 不能签** ⇒ ★main 本机只读 `/tmp/chain_offverify/s1_straight.kicad_pcb` "
    "(md5 `8b33af5181e8d80ef471c6d1f59298e6` · 命中 02 号件记的 stage-1 md5) 重跑 `state/check_pcb_drc.py` ⇒ "
    "落 `logs/iss337/16_official_s1_drc.txt` (★C1~C7 全过 · viol=0 · unc=54 · rc=0 · 与交卷页声称逐字一致 · **零写板**★) ⇒ "
    "★交卷页件数 22 → 23 件 (6 处同步) + §B8 补第 16 行 + 如实记明补证经过 (★不改成 agent 产出★)★ ⇒ "
    "★补后复检: 全部引用 0 MISS · 件数 23 == 盘面 23 · gate_check 仍 rc=0 (Q1 18/18)·板指纹仍未动★ "
    "★ **main 裁了它交回的 3 条 need (机制地界·不占老板拍板面·已答进 pm.yaml)**: ① `iss337_band_truth_overrides_doc` ⇒ "
    "**采纳** (★band 唯一真值 = 脚本 L59-61: 归一化段数 [2300,3200] · 铜长 [4600,5900]mm · 过孔 [380,520] · 老三区间全部作废★) "
    "② `iss337_need4b_two_way_copper_list` ⇒ **采纳** (★判据 = 逐网铜量名单 + 零铜网名单 **双向** · "
    "段数对齐 ≠ 同一块铜 (官方 vs best_unc23 86 条有铜网只相符 21 条) · 闸顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好★) "
    "③ `iss337_rereread_zerocopper_denominator` ⇒ **采纳** (★「布线 45→0」的分母必须在板那一趟的新基线上重读 · "
    "官方 24 条零铜里 21 条在 v76mg1 已有铜 · 两边都零铜只剩 3 条: `CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` ⇒ "
    "**24 不能直接当布线目标清单**★) ★ **★口径确认 (★沿用 main 20:5x 已裁口径·不重开★)**: 24 条里 "
    "**必需 23 条 = 15 差分腿 + 8 条单端脚** (`CAM_RESET_N` / `LED_G_D` / `USB_CC2` / `JTAG_TDI` / `UART_RX` / "
    "`SPI_MISO_BOOT` / `SPI_MOSI_BOOT` / `SPI_SCLK_BOOT`) · **可悬空 1 条 `FSIN_OUT`** · 待定 0 "
    "★ **未代老板拍板**: 板框 / 屏版本 / 跌落等级 / 7 个决策字母 (W-2 / W-1c / A4 / A5 / W-3 / U-1 / P7) 一个都没碰 ★ "
    "★ **零外发** ★ **零改闸** (gate_check.py / compare_arm_official.py / chain_gate.py md5 不变) ★ **零改真生成器** ★ "
    "★ **零落表** (网表 / 脚表 / BOM 三个 md5 不变) ★ **零写板** ★ **零改动别人分片** (只写 main 自己的 pm.yaml) ★"
)

src = open(LOG, encoding="utf-8").read()
i = src.find("\n- id: ISS-337")
j = src.find("\n- id: ISS-338")
if i < 0 or j < 0 or j < i:
    sys.exit("X ISS-337 段没定位到, 不落盘")
seg = src[i:j]
if "  status: fixing" not in seg:
    sys.exit("X ISS-337 status 不是 fixing, 不落盘 (可能已被别的 job 签过)")
new_seg = seg.replace("  status: fixing", "  status: verified", 1)
new_seg = new_seg.replace("  verify_result: null", "  verify_result: %r" % (VERIFY,), 1)
new_seg = new_seg.replace("  verify_date: null", "  verify_date: '2026-11-22'", 1)
if new_seg == seg:
    sys.exit("X 替换没生效, 不落盘")
bak = LOG + ".bak_%s_main_sign337" % STAMP
shutil.copy2(LOG, bak)
atomic_write(LOG, src[:i] + new_seg + src[j:])
print("★ ISS-337 签收落盘 · status: fixing → verified")
print("★ 备份: %s" % bak)

# ---------------------------------------------------------------- ② 裁 3 条 need (pm.yaml)
ANSWERS = [
    (
        "iss337_band_truth_overrides_doc",
        "★★【main 裁 (2026-11-22 21:2x · 机制地界)】★★ ★**裁决 = 采纳: band 唯一真值 = "
        "`tmp/iss337/seg_parity_selfcheck.py` L59-61 ⇒ 归一化段数 ∈ [2300, 3200] · 铜长 ∈ [4600, 5900] mm · "
        "过孔 ∈ [380, 520] ⇒ ★文档里的 [2400,2900] / [5400,5900] / [380,450] 三个老区间【全部作废】** ★ "
        "★★[实测] main 本机独立复跑 (21:1x) `tmp/iss337/seg_parity_selfcheck.py --selftest` ⇒ 末行 `ALL TESTS PASS` · rc=0★★: "
        "五块同工艺板全在带内 = 官方终板 2649/433/5726.9 · 官方 stage-1 2537/408/5563.9 · 现役 v76mg1 2582/471/5582.8 · "
        "v76mz 3099/486/5426.6 · iss325ctl 3129/505/5483.9 ⇒ ★**老口径会把官方板自己拦掉** (老段数 [2400,2900] 拦 v76mz 3099 / "
        "iss325ctl 3129 · 老过孔 [380,450] 拦现役臂 471/486/505 · 老铜长 [5400,5900] 拦 baseline_v76 4666.4) ⇒ "
        "★**区间不能由单块板锚定, 必须由「官方 + 现役 + v76mz + best_unc23」四块一起锚** ★ "
        "★落点 (机制地界·不占老板拍板面)★: ① `state/compare_arm_official.py` **不用改代码** (它本来就不比较段数) ⇒ "
        "只需在它前面加一道【可比性前置闸】, 判据 = 上面那三项区间, 越界即拦 ⇒ ★**不许拿不可比的板刷闸的结论** ★ "
        "② 归一化口径 = V1 (层, 网, 宽 + 度数=2) ⇒ 官方 2649 vs 现役 2582 (差 2.5%) ⇒ "
        "★**归一化段数只作【可比性闸】, 不作【优劣尺子】** ★ ⇒ ★**这条 need 从此闭合** ★",
        "tmp/iss337/seg_parity_selfcheck.py L59-61 · logs/iss337/18_norm_impl_diff.txt · "
        "logs/iss337/20_seg_parity_selftest_cont2.txt · logs/iss337/21_band_truth_and_why_changed.txt",
    ),
    (
        "iss337_need4b_two_way_copper_list",
        "★★【main 裁 (2026-11-22 21:2x · 机制地界)】★★ ★**裁决 = 采纳「双向名单」判据: ① 逐网铜量名单 + "
        "② 零铜网名单, 两张都要 ⇒ 不许拿归一化段数当唯一尺子** ★ "
        "★★[实测] 依据 (★ISS-337 自己的复算·main 已独立核对名单来源★)★★: 官方板 vs "
        "`state/.lastgood/best_unc23_clrfix.kicad_pcb` 两板都有铜的网 = 86 条 ⇒ "
        "★**逐网铜长相符 (±2% 或 1mm 内) 只有 21 条 ⇒ 65 条对不上** ⇒ "
        "★**⇒ 「段数对齐」≠「同一块铜」⇒ 拿段数当尺子会把两块不同的板判成同一块** ★ "
        "★落点 (机制地界)★: ① 名单制闸 `state/compare_arm_official.py` **不用改代码** ⇒ 参照板换成【现役同工艺基线板】即可 ⇒ "
        "② 前置加【可比性闸】 (★归一化段数 [2300,3200] · 铜长 [4600,5900]mm · 过孔 [380,520]★) ⇒ "
        "③ ★**闸的判据顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好** ★ ⇒ "
        "★**「unconnected 变少」不等于板子更好** (★把有铜的腿砍成零铜 ⇒ ratsnest 变少, 板子更烂★) ★ "
        "⇒ ★**这条 need 从此闭合** ★",
        "logs/iss337/17_main_findings_recheck.txt · logs/iss337/06_pernet_official_vs_current.txt · "
        "HW/PCB/ONETRIP_S8_SEGMENT_PARITY_ROOTCAUSE.md §4/§5 · state/compare_arm_official.py",
    ),
    (
        "iss337_rereread_zerocopper_denominator",
        "★★【main 裁 (2026-11-22 21:2x · 机制地界)】★★ ★**裁决 = 采纳: 「布线 45→0」的分母必须在"
        "【板那一趟的新基线】上重读 ⇒ ★官方板那 24 条零铜网【不能直接当布线目标清单】** ★ "
        "★★[实测] 三板对照 (★官方 24 / 现役链终 v76mg1 7 / v76mz 12 / best_unc23 7★)★★: "
        "★**官方板 24 条里 21 条在 v76mg1 上【已经有铜】⇒ 两边都零铜只剩 3 条**: "
        "`CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` ★ "
        "★重读办法 (板那一趟开工前执行·★在那一趟实际采用的基线板上跑·不是拿旧数推★)★: "
        "① 用那一趟的真实基线板跑 unconnected 清单 ⇒ 得分母 N' (★不是 45★) ② 逐条标 [必需 / 可悬空 / 待定] + "
        "标该网在新基线上有没有铜 ③ ★**必需性分级沿用 main 2026-11-22 20:5x 已裁口径 (不重开)★**: "
        "必需 = ★**15 差分腿 + 8 条单端脚**★ (`CAM_RESET_N` / `LED_G_D` / `USB_CC2` / `JTAG_TDI` / `UART_RX` / "
        "`SPI_MISO_BOOT` / `SPI_MOSI_BOOT` / `SPI_SCLK_BOOT`) · 可悬空 = ★**1 条 `FSIN_OUT`**★ · 待定 = 0 ⇒ "
        "★**⇒ 24 条里 23 条必需 + 1 条可悬空** ★ "
        "★★铁律 (★不许乐观过头★)★★: ★**「新基线靶更小」≠「新基线更好」** ★ ⇒ "
        "★**现役链终板自己过不了名单制闸 (退铜/孤岛) ⇒ 靶更小只是【工作量口径】变了, 不是【板子质量】变好了** ★ "
        "⇒ ★**这条 need 从此闭合 (★执行动作挂在板那一趟开工前·不占老板拍板面★)** ★",
        "logs/iss337/17_main_findings_recheck.txt · logs/iss337/25_netclass_itemwise_dump.txt · "
        "state/fragments/pm.yaml answers (iss338_* 三条已裁口径) · ★板那一趟开工前重读",
    ),
]

for key, value, ref in ANSWERS:
    spec = "key=%s to=hw-lead value=%s ref=%s" % (
        key, shlex.quote(value), shlex.quote(ref))
    cmd = [sys.executable, os.path.join(PROJ, "state/frag_write.py"),
           "--agent", "main", "--add-answer", spec]
    r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
    print("★ %s ⇒ rc=%d %s" % (key, r.returncode, (r.stdout or r.stderr).strip()[:200]))
    if r.returncode != 0:
        sys.exit("X frag_write 失败: %s" % key)

print("★ 全部落盘完成")
