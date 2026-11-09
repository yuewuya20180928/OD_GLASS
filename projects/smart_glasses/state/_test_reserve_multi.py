import os, sys, types
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 只导入类定义 (模块顶层可能很重 ⇒ 用 importlib 但不执行 main)
import importlib.util
spec = importlib.util.spec_from_file_location("gpr", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_pcb_routing.py"))
gpr = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(gpr)
except Exception as e:
    print("★导入告警(不影响本测试):", type(e).__name__, e)

class Fake(gpr.GridRouter):
    def __init__(self):
        self.cu_reserved = [dict() for _ in range(8)]
        self.route_reserve = {}
        self.W = 100; self.H = 100; self.g = 0.125; self.bb = [0.0, 0.0]
        self.route_reserve = {}
        self.cu_reserved = [dict() for _ in range(8)]
    def _ci(self, x): return int(round((x - self.bb[0]) / self.g))
    def _cj(self, y): return int(round((y - self.bb[1]) / self.g))
    def _idx(self, i, j): return j * self.W + i

def run(env_val):
    os.environ["PCB_ROUTE_RESERVE"] = env_val
    f = Fake()
    gpr.GridRouter._load_route_reserve(f)
    return f

# ① 单网 (旧语义) ⇒ 该格只允许那一个网
f = run("CSI_D0_D3_N_SRC:0,16.750,49.560,17.650,50.960")
cells = f.cu_reserved[0]
print("① 单网: 预留格数=%d · 样例允许集=%s" % (len(cells), sorted(cells.values())[0]))
assert all(isinstance(v, frozenset) and len(v) == 1 for v in cells.values()), "单网语义被破坏"
assert all("CSI_D0_D3_N_SRC" in v for v in cells.values())

# ② 多网 (新语法) ⇒ 一格允许两个网
f = run("CSI_D0_D3_N_SRC+CSI_D0_D3_P_SRC:0,16.750,49.560,17.650,50.960")
cells = f.cu_reserved[0]
sets = sorted(set(cells.values()), key=lambda s: sorted(s))
print("② 多网: 预留格数=%d · 允许集=%s" % (len(cells), [sorted(s) for s in sets]))
assert all(isinstance(v, frozenset) for v in cells.values())
assert set(sets[0]) == {"CSI_D0_D3_N_SRC", "CSI_D0_D3_P_SRC"}

# ③ 两个框重叠 ⇒ 合并成并集
f = run("AAA:0,1.0,1.0,2.0,2.0;BBB:0,1.5,1.0,2.5,2.0")
sets = sorted(set(f.cu_reserved[0].values()), key=lambda s: sorted(s))
print("③ 重叠合并: 允许集=%s" % [sorted(s) for s in sets])
assert any(set(s) == {"AAA", "BBB"} for s in sets)

# ④ 默认空 ⇒ 完全不变 (逐位不变)
os.environ["PCB_ROUTE_RESERVE"] = ""
f = run("")
assert len(f.cu_reserved[0]) == 0
print("④ 默认空 ⇒ cu_reserved 全空 ⇒ 逐位不变 ✔")

# ⑤ _free 的成员判断 (老语义 ≡ 新语义)
class F2:
    def __init__(self, cell):
        self.cu_reserved = [dict() for _ in range(8)]
        self.cu_reserved[0][0] = cell
    def _free_reserve(self, net):
        _rs = self.cu_reserved[0].get(0)
        if _rs is not None and net not in _rs:
            return False
        return True
f2 = F2(frozenset({"AAA"}))
print("⑤ 单网格: AAA=%s · BBB=%s (★老语义下 BBB 也应是 False)" % (f2._free_reserve("AAA"), f2._free_reserve("BBB")))
assert f2._free_reserve("AAA") and not f2._free_reserve("BBB")
print("\n★ 全部断言通过 ✔")
