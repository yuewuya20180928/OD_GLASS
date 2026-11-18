"""★2026-11-05 13:20 **cleanup_geometry 新逻辑的单元测试** (★语法通过 ≠ 逻辑对)
   验三件事:
     ① 挂在"孤立过孔"上的短铜 ⇒ 过孔被删后, 那段铜也要被删 (★不动点迭代)
     ② 端点落在**别网**过孔上的铜段 ⇒ 必须删 (★原来不算"接上" ⇒ 漏成悬空)
     ③ 正常连着的铜段 / 挂在同网过孔上的铜段 ⇒ 必须保留 (★别误删)
"""
import sys, os
sys.path.insert(0, "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state")
os.environ.setdefault("PCB_BOARD_W", "160")
os.environ.setdefault("PCB_BOARD_H", "100")
import pcbnew
import gen_pcb_routing as G

b = pcbnew.CreateEmptyBoard()
r = G.GridRouter(b)

# ── 场景 ───────────────────────────────────────────────
# 焊盘: GND 焊盘一块 (10,10)-(11,11) 在 F.Cu
r.pad_rects_l.append(("GND", 10.0, 10.0, 11.0, 11.0, (0,)))
# ★首尾相接那两段的两端都落在焊盘上 ⇒ 才是"真连着"
r.pad_rects_l.append(("GND", 19.5, 19.5, 20.5, 20.5, (0,)))
r.pad_rects_l.append(("GND", 21.5, 19.5, 22.5, 20.5, (0,)))

# ③-好: 焊盘 → 过孔 (同网) 的正常铜 (保留)
r.tracks.append(("GND", 10.5, 10.5, 10.5, 12.0, 0, 0.25))
r.vias.append(("GND", 10.5, 12.0, 0, 5))

# ③-好: 两段首尾相接 (同网同层) ⇒ 两端都接上 (保留)
r.tracks.append(("GND", 20.0, 20.0, 21.0, 20.0, 0, 0.25))
r.tracks.append(("GND", 21.0, 20.0, 22.0, 20.0, 0, 0.25))

# ①-坏: 焊盘 → (不存在/会被删的) 过孔 的短铜 ⇒ 过孔删了, 铜必须跟着删
r.tracks.append(("GND", 30.0, 30.0, 30.0, 30.5, 0, 0.25))
r.vias.append(("GND", 30.0, 30.5, 0, 5))     # 孤立过孔 (没有任何段端在它上面? 其实有 ⇒ 见下)

# ②-坏: 端点落在**别网**过孔上 ⇒ 必须删
r.vias.append(("SIG", 40.0, 40.0, 0, 5))
r.tracks.append(("GND", 40.0, 40.0, 41.0, 40.0, 0, 0.25))

before = len(r.tracks)
nz, nd, nv = r.cleanup_geometry(verbose=True)
print("清理前 段=%d 孔=%d" % (before, len(r.vias) + nv - nv))
print("清理后 段=%d 孔=%d   (删零长 %d / 删悬空 %d / 删孤立孔 %d)"
      % (len(r.tracks), len(r.vias), nz, nd, nv))
for t in r.tracks:
    print("   留下:", t)
for v in r.vias:
    print("   留下孔:", v)

ok = True
def _chk(cond, msg):
    global ok
    print(("  ✔ " if cond else "  ✘ ") + msg)
    if not cond:
        ok = False

def _has(t):
    return any(a[0] == t[0] and abs(a[1]-t[1])<1e-6 and abs(a[2]-t[2])<1e-6
               and abs(a[3]-t[3])<1e-6 and abs(a[4]-t[4])<1e-6 for a in r.tracks)

_chk(_has(("GND", 10.5, 10.5, 10.5, 12.0, 0, 0.25)), "③ 同网焊盘→过孔的铜: 保留")
_chk(_has(("GND", 20.0, 20.0, 21.0, 20.0, 0, 0.25)), "③ 两端都落在焊盘上的链段1: 保留")
_chk(_has(("GND", 21.0, 20.0, 22.0, 20.0, 0, 0.25)), "③ 首尾相接的第二段: 保留")
_chk(not _has(("GND", 30.0, 30.0, 30.0, 30.5, 0, 0.25)), "① 孤立孔上的短铜: 已删")
_chk(not _has(("GND", 40.0, 40.0, 41.0, 40.0, 0, 0.25)), "② 端点落在别网过孔上的铜: 已删")
# ── _via_center_ok (治 hole_to_hole) ────────────────────
r.vias.append(("GND", 50.0, 50.0, 0, 5))
r.vias.append(("SIG", 50.25, 50.0, 0, 5))     # 中心距 0.25mm ⇒ 太近
r.vias.append(("SIG", 50.6, 50.0, 0, 5))      # 中心距 0.60mm ⇒ 合法 (>= 0.58)
_chk(r._via_center_ok(50.25, 50.0) is False, "孔中心距 0.25mm ⇒ 判不合格 (治 hole_to_hole)")
_chk(r._via_center_ok(50.3, 50.0) is False, "孔中心距 0.30mm ⇒ 判不合格")
_chk(r._via_center_ok(52.0, 50.0) is True,  "离所有孔都远 ⇒ 判合格")
# ★★2026-11-05 20:38 **异网孔距已提到 0.80mm (铜到铜)** ⇒ ★0.59mm 对异网**不再合格**
_chk(r._via_center_ok(51.19, 50.0) is False, "孔中心距 0.59mm (异网) ⇒ 判不合格 (异网要 0.80mm)")
_chk(r._via_center_ok(51.41, 50.0) is True,  "孔中心距 0.81mm (异网) ⇒ 判合格 (>= 0.80mm)")

# ★★★2026-11-05 20:38 **防回归**: "焊盘内直接落孔"那条路径必须走 `_via_exact_ok`
#   ★**实测 v34_R 唯一那条 DRC clearance 的根因**: GND 孔 @ (62.70,64.45) 压住 I2C_B_SCL 走线
#   ⇒ ★**这条分支原来从不查几何净距** ⇒ ⇒ 别的网走线从孔边擦过去也不管
_src = open(G.__file__, encoding="utf-8").read()
_i = _src.find("if self._in_pad(px, py):")
_seg = _src[_i:_i + 2600] if _i >= 0 else ""
_chk(_i >= 0 and "_via_exact_ok" in _seg,
     "★ in-pad 落孔分支必须调 _via_exact_ok (防 v34_R 那条 clearance 回归)")

# ── ★★2026-11-05 13:58 **同网孔间距** (★真根因: _via_exact_ok 的 ③ 写了"同网不算") ──
#   ★**实测 v30_P 唯一那条 DRC**: 两个 **GND** 孔 @24.45/24.95 (中心距 0.50mm, 净距 0.2000mm)
#   ⇒ ★**孔到孔是制造规则, 不分网** ⇒ 同网的两个孔也必须卡 0.60mm 中心距
_r2 = G.GridRouter(pcbnew.CreateEmptyBoard())
_r2.vias.append(("GND", 24.45, 60.2, 0, 5))
_chk(_r2._via_exact_ok(24.95, 60.2, 0.5, "GND", 0.3) is False,
     "★ 同网两孔中心距 0.50mm ⇒ _via_exact_ok 判不合格 (同网不能豁免!)")
_r2.vias.append(("GND", 26.0, 60.2, 0, 5))
_chk(_r2._via_exact_ok(26.9, 60.2, 0.5, "GND", 0.3) is True,
     "离所有孔都远 (0.9mm / 2.45mm) ⇒ 判合格")

# ── ★★cleanup 兜底: 中心距不够的孔, 后落的那个必须被删 ──
_r3 = G.GridRouter(pcbnew.CreateEmptyBoard())
# ★**两个焊盘 + 各一根短铜引到各自的孔** (★真实场景: v30_P 那两个孔都是这样来的)
#   ⇒ ★**不是孤立孔** (孤立孔会被"删孤立过孔"那一步先删掉, 测不到间距逻辑)
_r3.pad_rects_l.append(("GND", 24.00, 59.90, 24.60, 60.50, (0,)))
_r3.pad_rects_l.append(("GND", 25.20, 59.90, 25.80, 60.50, (0,)))
_r3.vias.append(("GND", 24.45, 60.2, 0, 5))
_r3.tracks.append(("GND", 24.45, 60.2, 24.30, 60.2, 0, 0.25))   # 孔 A → 焊盘 A
_r3.vias.append(("GND", 24.95, 60.2, 0, 5))                      # 与孔 A 中心距 0.50mm ⇒ 太近
_r3.tracks.append(("GND", 24.95, 60.2, 25.50, 60.2, 0, 0.25))   # 孔 B → 焊盘 B
_nz3, _nd3, _nv3 = _r3.cleanup_geometry(verbose=False)
_chk(len(_r3.vias) == 1, "★ cleanup 兜底: 中心距 0.50mm 的同网两孔 ⇒ 删掉后落的那个 (剩 %d 个)" % len(_r3.vias))
_chk(abs(_r3.vias[0][1] - 24.45) < 1e-6 and abs(_r3.vias[0][2] - 60.2) < 1e-6,
     "★ cleanup 兜底: 保留的是先落的那个 (24.45,60.2)")

# ── ★★2026-11-05 21:40 **窄焊盘边缘落孔的回归防护** (★v35_R 实测 DRC 2 的真根因) ──
#   ★**实测**: U_TEMP.2 (焊盘短边 <0.55mm) 的环格 (62.700,64.450) 落了 Ø0.5 孔
#     ⇒ 孔心离焊盘中心仅 0.201mm ⇒ 孔探出焊盘铜 ⇒ 离邻居 I2C_B_SCL 短桩 0.50mm
#     ⇒ 净距 0.125mm ⇒ DRC clearance 违规 ×2 (同一颗孔, KiCad 按线段各报一次)
#   ★**修法**: ① in-pad 分支加"焊盘短边 ≥ 孔径+0.10"门槛 ② 三遍成功都登记 done_pads
#     ⇒ ★**同一个焊盘绝不落两个孔** (冗余孔还可能压住别人的逃逸短桩)
_chk("_pad_rect_at" in _src, "★ 路由器必须有 _pad_rect_at (查这个点属于哪个同网焊盘)")
_i2 = _src.find("if self._in_pad(px, py):")
_seg2 = _src[_i2:_i2 + 6000] if _i2 >= 0 else ""
_chk("_pad_rect_at(px, py, net_g)" in _seg2,
     "★ in-pad 分支必须先查 _pad_rect_at (知道孔落在哪个焊盘 ⇒ 才能判尺寸)")
_chk("_pshort < _dia + 0.10" in _seg2,
     "★ in-pad 分支必须有'焊盘短边 ≥ 孔径+0.10'门槛 (窄焊盘不许边缘落孔)")
_chk("done_pads.append(pad)" in _seg2,
     "★ in-pad 分支成功后必须登记 done_pads (第二/三遍不许再给这个焊盘落孔)")
# ★★第二遍(chain) 与 第三遍(in-pad) 也必须登记 ⇒ 三个分支共 3 处
_chk(_src.count("done_pads.append(pad)") >= 3,
     "★ done_pads.append(pad) 至少 3 处 (第一遍in-pad / 第二遍chain / 第三遍in-pad)"
     " —— 实测 %d 处" % _src.count("done_pads.append(pad)"))
# ★★第三遍的尺寸门槛必须 ≥ 孔径+0.10 (原来是 0.55 ⇒ 孔探出铜面)
_i3 = _src.find('why["inpad_small"]')
_seg3 = _src[max(0, _i3 - 400):_i3 + 60] if _i3 >= 0 else ""
_chk("VIA_DIA_S + 0.10" in _seg3,
     "★ 第三遍尺寸门槛必须是 VIA_DIA_S+0.10 (0.60) 而不是 0.55 (孔探出铜面)")

# ── ★★2026-11-05 21:40 **_pad_rect_at 的功能自测** ──
_r4 = G.GridRouter(pcbnew.CreateEmptyBoard())
_r4.pad_rects_l.append(("GND", 62.70, 64.20, 63.10, 64.80, (0,)))
_r4.pad_rects_l.append(("I2C_B_SCL", 62.70, 63.55, 63.10, 64.15, (0,)))
_pr4 = _r4._pad_rect_at(62.90, 64.50, "GND")
_chk(_pr4 is not None and abs(_pr4[0] - 62.70) < 1e-6 and abs(_pr4[3] - 64.80) < 1e-6,
     "★ _pad_rect_at 在同网焊盘里 ⇒ 返回该焊盘矩形 (GND @62.90,64.50)")
_chk(_r4._pad_rect_at(62.90, 63.85, "GND") is None,
     "★ _pad_rect_at 落在别网焊盘里 ⇒ 返回 None (不认别网的焊盘)")
_chk(_r4._pad_rect_at(70.00, 70.00, "GND") is None,
     "★ _pad_rect_at 落在空处 ⇒ 返回 None")

# ── ★★2026-11-05 22:5x **v36_S 窄焊盘孔心回归防护** ──
# ★**实测依据**: `U_TEMP.2` 焊盘 0.45x0.30 (短边 0.30 ⇒ Ø0.5 孔必然探出铜面 ★**不是错**)
#   ⇒ v35 的 DRC 2 真因 = 孔心偏心 0.195mm ⇒ 压住邻居 I2C_B_SCL 的逃逸短桩 ⇒ 净距 0.125
#   ⇒ 焊盘中心 ⇒ 净距 0.2085 ✔ ; ★**吸附 0.25 栅格 (62.95,64.45) ⇒ 0.184 ✘** ⇒ 必须精确坐标
_chk("_narrow_pad_candidates" in _src,
     "★ 路由器必须有 _narrow_pad_candidates (窄焊盘挑余量最大的孔心)")
_chk("_place_in_pad_via" in _src,
     "★ 路由器必须有 _place_in_pad_via (窄焊盘落孔的公共路径)")
_chk("def _via_room_score" in _src,
     "★ 路由器必须有 _via_room_score (落点余量分 ⇒ 挑最宽松的位置)")
_i4 = _src.find("def _place_in_pad_via")
_seg4 = _src[_i4:_i4 + 2500] if _i4 >= 0 else ""
_chk("_via_exact_ok(px, py, dia, net_g, drill)" in _seg4,
     "★ _place_in_pad_via 必须调 _via_exact_ok (别网铜/孔距/净距)")
_i5 = _src.find("def _narrow_pad_candidates")
_seg5 = _src[_i5:_i5 + 2500] if _i5 >= 0 else ""
_chk("cx + _ox" in _seg5 and "cy + _oy" in _seg5,
     "★ 窄焊盘孔心必须用**精确坐标** (cx+偏移) ⇒ 不许吸附 0.25 栅格 (实测 0.184 ✘)")
_chk("_pad_rect_at(_px, _py, net) is None" in _seg5,
     "★ 窄焊盘候选孔心必须在焊盘铜内 (不许跑到焊盘外)")
_chk("_via_room_score" in _seg5,
     "★ 窄焊盘候选必须按余量分排序 (挑最宽松的位置)")

# ── ★★功能自测: 窄焊盘候选点必须比"环格偏心点"更远离别网焊盘 ──
_r5 = G.GridRouter(pcbnew.CreateEmptyBoard())
# U_TEMP.2 真实几何: GND 焊盘 0.45x0.30 @ (62.895,64.500); 邻居 I2C_B_SCL 在正上方 0.65
_r5.pad_rects_l.append(("GND", 62.670, 64.350, 63.120, 64.650, (0,)))
_r5.pad_rects_l.append(("I2C_B_SCL", 62.670, 63.700, 63.120, 64.000, (0,)))
_c5 = _r5._narrow_pad_candidates(62.895, 64.500, "GND", 0.50, [])
_chk(len(_c5) == 1,
     "★ 窄焊盘必须给出 1 个候选落点 (实测 %d 个)" % len(_c5))
if _c5:
    _px, _py = _c5[0]
    _chk(_r5._pad_rect_at(_px, _py, "GND") is not None,
         "★ 候选孔心必须在 GND 焊盘铜内 (%.3f,%.3f)" % (_px, _py))
    _s_new = _r5._via_room_score(_px, _py, 0.50, "GND")
    _s_old = _r5._via_room_score(62.700, 64.450, 0.50, "GND")
    _chk(_s_new > _s_old,
         "★ 候选孔心余量必须优于 v35 的偏心环格 (新 %.4f > 旧 %.4f)" % (_s_new, _s_old))
    _chk(abs(_px - 62.895) < 0.11 and abs(_py - 64.500) < 0.11,
         "★ 候选孔心必须贴着焊盘中心 (不许跑到盘外) (%.3f,%.3f)" % (_px, _py))


print("★测试结果:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
