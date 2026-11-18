import importlib.util, sys
P="/home/yuewuya/.openclaw/workspace/projects/smart_glasses/MECH/hinge_usb_check.py"
spec=importlib.util.spec_from_file_location("huc_before", P)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.RECOMMENDED_PINS["J_CHG"]=8   # ★只回退 J_CHG 脚数这一个变量 (改前口径), 其余一律不动
sys.argv=["hinge_usb_check.py"]
sys.exit(m.main())
