#!/usr/bin/env python3
"""ISS-356 cont2 · 分片写入驱动 (★只调 state/frag_write.py, 不自己写分片★)
★纪律: state/fragments/hw.yaml 的写入**只**由 state/frag_write.py 做 (原子写)★
★本脚本只负责把长文本安全地包成 key="value" 规格串 (frag_write 用 shlex.split 解析)★
"""
import subprocess
import sys
import os

ROOT = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
FRAG = os.path.join(ROOT, 'state', 'frag_write.py')


def spec(**kv):
    """把 dict 变成 frag_write 认的 'k="v" k2="v2"' 串 (值里的直引号换成中文引号)"""
    out = []
    for k, v in kv.items():
        v = str(v).replace('"', '＂')
        out.append('%s="%s"' % (k, v))
    return ' '.join(out)


def run(args):
    cmd = [sys.executable, FRAG, '--agent', 'hw-lead'] + args
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(p.stdout.strip())
    if p.stderr.strip():
        print(p.stderr.strip(), file=sys.stderr)
    if p.returncode != 0:
        raise SystemExit('frag_write rc=%d' % p.returncode)
    return p.stdout


ARTIFACTS = [
    dict(path='HW/FP_TRUTH_BASELINE.md', kind='baseline', version='iss356-cont2',
         summary='★ISS-356 封装真值基线页 (新建)★ · §1 族级映射表 (板面 186 占位封装按 焊盘编号+焊盘尺寸+fab外框 聚成 24 族, 靶子内 4 族各给候选真库封装 + 三判据核对 + 分档依据 + 证据等级 + 降级方案) · §2 逐 ref 表 78 件 (镜脚主PCB 必装 ∩ 非NET/TP ∩ footprint待定) 每行 12 栏含 目标lib:name + 库文件路径 + md5 + 焊盘数网络核对 + 候选OPN + 证据等级 + 是否触发布局布线改动 + 降级方案 · §3 删件候选 5 组 (只给候选与代价, 不代拍) · §4 镜框充电板 22 件只登记 + 跨界 3 件事实 · §5 已做未做 + 续做入口 · 页头三句写死 (本页是封装真值基线不替代选型页 / 零写板 / 本单不落表) · 附机器可读基准块 (records 78 条)'),
    dict(path='HW/check_fp_truth_baseline.py', kind='gate', version='iss356-cont2',
         summary='★ISS-356 本单自带只读闸 (新建)★ · C0 基准块合法JSON · C1 靶子覆盖 (口径由脚本自己跑CSV: 必装∩非NET/TP∩待定 = 100 ⇒ 主PCB 78 + 充电板 22; 78件须在§2带目标lib:name, 22件须在§4.1登记, 漏一个点名) · C2 每个lib:name的 .kicad_mod 文件本体实测在盘 + md5 一致 (★查文件不是只查库目录★) · C3 证据等级非空且 ∈ 五级白名单 (写[官方] = 红) · C4 降级方案非空且非占位词 · C5 禁等原厂回信类挂起措辞 (5词黑名单 + skip区) · C6 件数三方自洽 (脚本实跑 = 基准块counts = records ref集合) · --selftest 6 条反向用例每条自证红的是目标那一条其余仍绿, 末行 ALL TESTS PASS, 沙盒落项目盘 tmp/ 跑完即删 ⇒ 真件零污染 · ★闸自己抓到并修掉 3 个真bug (C6与C1耦合 / M3M4列索引错位 / M5探针串原本就在文档里)★'),
    dict(path='HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md', kind='handoff', version='iss356-cont2',
         summary='★ISS-356 交卷页 (新建)★ · B1 结论 (78件封装真值 100%给出 + 挖出 3 类板面硬缺陷) · B2 验收标准自评 (F1~F17 逐条自跑 + C1~C6 逐条 + selftest 6/6 + 6 项未验诚实登记) · B3 证据分级 (五级白名单零[官方]) · B4 接口取值声明 (12条, 只对封装层取值, 不代拍) · B5 未决项与卡点 (9条卡点 + ★两次死亡: cont0 被abort / cont1 08:47:16 被 50 分钟 runTimeout 掐死★ + 自我限定 5 条) · B6 自证复现命令 (7 组原样输出)'),
    dict(path='logs/iss356/', kind='log', version='iss356-cont2',
         summary='★ISS-356 证据留档★ · parse_board2.py (板面186封装 + pad网络 + fab外框; ★修掉 cont1 版 parse_board.py 漏采 pad.net 的缺陷★) · probe_lib_fab.py (库封装 F.Fab / F.CrtYd 实测) · extract_target78.py (靶子口径 + 焊盘数网络核对, D1/D2 由此出) · build_fp_truth_baseline.py (基线页生成器, 只写 HW/FP_TRUTH_BASELINE.md) · board_footprints_v2.json + lib_fab_geom.json + target78_facts.json'),
]

CLAIMS = [
    dict(key='iss356_fp_truth_baseline',
         value='★ISS-356 cont2 交卷 (纯分析 · 零写板 · 零落表 · 零外发 · 零采购)★ · ★靶子口径 = 必装 ∩ 非NET/TP ∩ footprint待定 = 100 ⇒ 镜脚主PCB 78 件 (本单§2 必做范围, 100% 做完) + 镜框充电板 22 件 (§4 只登记不展开查库)★ · ★78 件每件都给出实测在盘的目标 lib:name (R → Resistor_SMD:R_0603_1608Metric / C → Capacitor_SMD:C_0603_1608Metric / 绿LED → LED_SMD:LED_0805_2012Metric / 红LED → LED_SMD:LED_0603_1608Metric / 排针 → Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical), 共 81 处 .kicad_mod 逐个 test -f + md5 核对在盘★ · ★挖出 3 类板面硬缺陷: D1 = C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2 四件 2 端子件板面只有 1 个 land (网表 2 脚, 脚2=GND) ⇒ 3 个 100nF 去耦接地悬空 + 电池检测分压链断 ⇒ 根因 = netlist_v1.csv 这 4 件接地行 net 栏写成信号网名, 生成器 derive_pads 按 (器件,网名) 去重只落 1 个 land (属落表批次地界, 本单只登记); D2 = R_PU_PG 焊盘序与网表脚序相反 (电阻无极性电气无影响, 但回填时须按网表脚号对齐 pad 号); D3 = J_DEBUG land pitch 0.50 vs 实物 1.27 差 0.77mm (E-1 已拍死, 板侧项在 ISS-343 B33_PIN_LAND_1P27, 本单不重复做, 只补一条 MECH 净距复核)★ · ★族级分档推理链: 占位 fab 外框 1.80×1.00 ⊇ 0603 本体 1.60×0.825 且 占位 land 中心距 1.60 ≈ 0603 官方 1.65 (Δ0.025/脚) ⇒ 走线端点几乎原地 ⇒ FAM-1 基线 0603; 0402 官方 land 1.02 ⇒ 71 件全重画; 0805 本体 2.00×1.25 超出占位外框 ⇒ 判据③不过★ · ★F15 口径差已定位: (1,2) 实为 107 (原写 105, 差 2 = C_VBUS_GND + J_CHG 即多余 2), (1,) 实为 49 (原写 7 = 只数真实器件, 排除 42 个 TP_*)★ · ★F14 的 SW_SPST_TL3342 实测不在盘 (KiCad 10 官方库无此封装; 靶子里无按键件故零影响)★ · ★F4/F5 的 129/123 是必装+非NET/TP 子集内口径, 全表实为 178/172 ⇒ 不是矛盾是口径不同★ · ★板指纹前后双证 md5 611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17.362193413 / 4,940,213 B 未变; 3 个真源 md5 未变★ · ★两次死亡: cont0 被 abort + cont1 08:47:16 被 50 分钟 runTimeout 掐死 (读数在盘交付物零) ⇒ 本轮先落 §1 + 闸再写 §2, 且 cont1 读数全部重跑复核 (cont1 的 parse_board.py 漏采 pad.net, 本轮 parse_board2.py 修掉, 这才使 D1/D2 能被发现)★',
         note='HW/FP_TRUTH_BASELINE.md · HW/check_fp_truth_baseline.py · HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md'),
    dict(key='iss356_gate_verdict',
         value='★ISS-356 自带闸 HW/check_fp_truth_baseline.py: 正常跑 rc=0 ALL CHECKS PASS (C0 基准块合法JSON / C1 78件靶子§2全覆盖 + 22件§4.1全登记 78-78 与 22-22 / C2 81处 lib:name 的 .kicad_mod 实测在盘 + md5 一致 / C3 81行证据等级全 ∈ 五级白名单 / C4 81行降级方案全非空且非占位词 / C5 正文无等原厂回信类挂起措辞 / C6 件数三方自洽 实跑 78-22-100 = 基准块 = §2表行数)★ · --selftest rc=0 末行 ALL TESTS PASS, 6 条反向用例全过且每条都自证【红的是目标那一条其余仍绿】: M1 删§2一行⇒C1 / M2 改 lib:name 成不存在⇒C2 / M3 清空证据等级⇒C3 / M4 清空降级方案⇒C4 / M5 正文塞等原厂回信⇒C5 / M6 篡改件数字段⇒C6 · 沙盒落项目盘 tmp/iss356_selftest 跑完即删 ⇒ 真件零污染★ · ★闸自己抓到并修掉 3 个真bug (C6 曾与 C1 被删一行同时触发 ⇒ 行数判据移进 C1; M3/M4 列索引错位 (split 后尾部 2 个空槽) ⇒ 按 len-4 / len-2 定位并在跑前自检列值; M5 探针串本来就在原文档里 ⇒ 改成探针必须在副本里且不在原文档里才算变异生效)★ · ★闸 C5 第一次跑就抓到基线页 §6 自己写的[等回复]一词 ⇒ 已改成[外部等待式挂起措辞]并重生成 ⇒ 不是靠改闸放水, 是把页改对★',
         note='HW/check_fp_truth_baseline.py'),
    dict(key='iss356_scope_and_boundary',
         value='★ISS-356 本单只锁封装真值 (哪块板上是哪个真库封装), 不锁料号 · 不落表 · 不写板 · 不外发 · 不代拍★ · 外部事实一律转引在盘页面 (ISS-241 §⑪~§⑭ / S15 / S16 / S19 + ISS-112) 并标[官网]+转引, 本轮未重新抓官网 · 未发任何询价邮件表单 · 未下单 ⇒ 凡查不到的件标[0数据] + 降级方案 (同封装官网等效件), 零挂起措辞★ · 不代拍项已登记不代裁: C_VBUS_GND 留位/下板 (归老板, 只登记事实) + U-1 画哪块板 + ESD 架构与型号轴 + LED 两颗对称性 (ISS-241 §⑬ 已留给 main, 本单沿用) + 删件 5 组候选 (TP_* 42 / LED 4 / R_SUPV_DIV 2 / C_AC_CSI 10 / C_KEY_CAM + R_NTC_BAT)★ · 充电板 22 件只登记不展开查库 (§4.1 逐条列出) · 靶外同族 3 件单 land 件 (CHG_GND_STAR 只有 1 脚 GND 故 1 land 是对的, 目标 TestPoint:TestPoint_Pad_D1.0mm; C_KEY_CAM 与 R_NTC_BAT 同病但 DNP) 只登记于 §2.2 不计入 78★ · 写盘范围只有 4 处 + logs/iss356/: HW/FP_TRUTH_BASELINE.md (新建) / HW/check_fp_truth_baseline.py (新建) / HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md (新建) / state/fragments/hw.yaml (走 frag_write.py) ⇒ 其余一字未动 (板 / 网表 / 脚表 / BOM / 原理图 / 别人分片 / state/gate_check.py 与 merge.py 均未改; 且未跑 gen_bom.py / gen_pcb_netlist_board.py / gen_kicad_sch.py / gen_production_pack.sh 任一重写真件的生成器)★',
         note='HW/FP_TRUTH_BASELINE.md §6 边界声明'),
]

NEEDS = [
    dict(key='iss356_netlist_4rows_gnd_fix', to='落表批次',
         item='★ISS-356 D1 根因 (落表批次地界, 本单零落表)★: HW/netlist_v1.csv 里 C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2 这 4 件的接地行把 net 栏写成了信号网名 (如 net=KEY_PWR node1=C_KEY_PWR node2=GND), 而正常写法是独立的 net=GND 行 (对照 C_BULK_SENSOR_CORE) ⇒ 板生成器 state/gen_pcb_netlist_board.py 的 derive_pads() 按 (器件, 网名) 去重 ⇒ 这 4 件只长出 1 个焊盘 ⇒ ★板面缺接地 land: 3 个 100nF 去耦电容接地端悬空 (去耦失效) + R_BAT_DET_2 是 BAT_DET 分压链下臂未接 GND (电池检测读数无意义)★ ⇒ ★请同批把这 4 行改成 net=GND node1=REF node2=GND★ ⇒ ★注意: 只按 ISS-356 §2 表的 0603 换封装救不了这 4 件 (0603 是 2 焊盘封装, 换上去会多出 1 个无网焊盘) ⇒ 必须先修网表★',
         since='2026-11-23'),
    dict(key='iss356_bom_footprint_backfill', to='落表批次',
         item='★ISS-356 交付的封装真值待回填 (本单零落表)★: 照 HW/FP_TRUTH_BASELINE.md §2 逐 ref 表的 目标 lib:name 列, 把 78 件的 BOM footprint 栏 + 原理图 Footprint 属性回填 (同批改 HW/netlist_v1.csv 那 4 行, 见 iss356_netlist_4rows_gnd_fix) ⇒ 重跑板生成器 ⇒ 板 md5 只变一次 ⇒ ★回填时按网表脚号对齐 pad 号 (坑: R_PU_PG 板面 pad 序与网表脚序相反, 见 ISS-356 交卷页 §B1.2 D2)★ ⇒ 回填完可直接用 python3 HW/check_fp_truth_baseline.py 当核对闸 (它只认页里的 78 行与库文件在盘, 不认回填结果 ⇒ 回填校验另需落表批次的闸)★',
         since='2026-11-23'),
    dict(key='iss356_charge_board_22_fp_truth', to='落表批次',
         item='★ISS-356 充电板 22 件封装真值债 (本单只登记, 未展开查库)★: 清单已在 HW/FP_TRUTH_BASELINE.md §4.1 逐条列出 (C_BAT / C_BST / C_PMID / C_SYS / C_VBUS_IC / D_CHG_LED / D_ESD_TC / D_TVS_VBUS / FB_VBUS / L_CHG / Q_CHG_LED / R_CC1 / R_CC2 / R_CE / R_CHG_LED / R_ILIM / R_OTG / R_PSEL / R_PU_CHG_STAT / R_PU_SCL / R_PU_SDA / R_STAR_PGND) ⇒ ★这 22 件本轮实测全部不在镜脚主 PCB 板面 (板面 grep BQ25896 = 0, U_CHG 不在板面) ⇒ 属另一块板 (镜框充电板), 不在本单靶子里★ ⇒ ★续做入口: 按 ISS-356 §1 同款三判据 (焊盘数 / 焊盘网络 / 本体+land 落进占位外框) 逐件查库定封装; §4.2 已转引 5 条现成结论 (U_CHG / Q_CHG_LED / D_TVS_VBUS / D_ESD_TC / FB_VBUS) 可直接接续★ ⇒ 若型号同时定了 ⇒ 板 md5 第二次变的风险同主板侧, 需并进同一趟',
         since='2026-11-23'),
    dict(key='iss356_jdebug_mech_clearance_recheck', to='mech-lead',
         item='★ISS-356 D3 引出的结构净距口径差 (MECH 域, 本单只报量差)★: J_DEBUG 的板侧 land 改动 (0.50 → 1.27mm pitch) 已由 E-1 拍死并登记在 ISS-343 的 B33_PIN_LAND_1P27 ⇒ 本单不重复做, 只给封装真值 Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical (4 通孔 @1.27, pad 1.0×1.0, 实测在盘)★ ⇒ ★但量差要核: HW/PCB/BOARD_ONEPASS_WORKPACKET.md §C-SEAT-1 的清空区是按 1.27 pitch + 0.275mm 宽 pad 算的 (X 宽 4.0850mm), 而官方 THT 排针 pad 宽 1.0mm ⇒ 铜箔净宽 4.81mm ⇒ 差 0.725mm ⇒ 请按官方 land 核清空区/开口/座体净距是否还过 (单边间隙与 CRIT 0.60 的关系)★ ⇒ 若改用 SMD 变体 (PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left) 则 land 变 2×2 交错而非 1×4 直排 ⇒ 结构尺寸要重算 (本单已把这条列为降级方案)',
         since='2026-11-23'),
    dict(key='iss356_dup2_and_f15_scope', to='main',
         item='★ISS-356 实读与 F15/§9-6-3 的两处口径差 (只报事实, 不代裁)★: ① 「多余 2」已定位 = 板面 186 vs BOM 镜脚主PCB 184 ⇒ 多出 C_VBUS_GND (BOM board 栏=镜框充电板, dnp=DNP) + J_CHG (BOM board 栏=跨铰链界面, type NET) ⇒ C_VBUS_GND 已有板侧项 B02_C_VBUS_GND, J_CHG 属跨铰链界面域 ⇒ 请认这两件 (另: C_VBUS_OUT 同属镜框充电板 + DNP 但本轮实测不在任何板面 ⇒ 不在多余 2 里) ② F15 的 (1,2)=105 / (1,)=7 是按 焊盘编号集 聚类且只数真实器件 (排除了 42 个 TP_*) ⇒ 本轮按 焊盘编号+焊盘尺寸+fab外框 聚类 = 24 族, 同按只数编号则 (1,2)=107 / (1,)=49 ⇒ ★请统一口径, 否则 板面账 (186) 与族聚类账对不上, 「板只改一次」的波及面会被低估★ ③ 另: F14 的 SW_SPST_TL3342 实测不在盘 (KiCad 10 官方 Button_Switch_SMD 库无此封装) ⇒ 本单靶子里无按键件故零影响, 但该事实链是否要在别的页订正请你定',
         since='2026-11-23'),
    dict(key='iss356_led_symmetry_and_delete_decisions', to='main',
         item='★ISS-356 登记的两个不代拍项 (交 main/老板裁决, 本单只给候选与代价)★: ① LED 两颗封装不对称: 本单沿用 ISS-241 §⑬ 的逐件推荐 (D_LED_G → LED_SMD:LED_0805_2012Metric, D_LED_R → LED_SMD:LED_0603_1608Metric) ⇒ 若改两颗同封装 (都 0805) ⇒ 代价 = 红件 OPN 要重查 (ISS-241 记 [0数据]) + G-5 亮度账要重算 + 落板批次要一套 land ⇒ ② 删件 5 组候选 (TP_* 42 个单 land 测试点 / 状态指示灯 4 件 / R_SUPV_DIV1+2 跳线位 / C_AC_CSI_* 10 件 / C_KEY_CAM + R_NTC_BAT) ⇒ 每组的 省掉什么 / 代价 / 删了会不会改板面 (占位焊盘还在 ⇒ 板 md5 再变一次) 已在 HW/FP_TRUTH_BASELINE.md §3 逐条列出 ⇒ ★注意 C_AC_CSI_* 那组的依据是 [0数据] (SoM 内部是否已做 AC 耦合本轮无证据) ⇒ 证据不足前不建议删★',
         since='2026-11-23'),
]

ANSWERS = [
    dict(key='iss356_fp_truth_scope', to='main',
         value='★ISS-356 答 main 的三个订正 + 一个 scope 问题★: ① 靶子口径 = 必装 ∩ 非NET/TP ∩ footprint待定 = 100 ⇒ 镜脚主PCB 78 + 镜框充电板 22; 本单 §2 100% 做完这 78 件, 另 22 件在 §4 只登记不展开查库 (续做入口见 §5.3) ② 本轮自己重跑了单焊盘清单: 板面 186 封装里 1 焊盘的 49 个 = TP_* 42 + 真实器件 7 (CHG_GND_STAR / C_KEY_CAM / C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2 / R_NTC_BAT) ⇒ 与你给的名单逐字一致 (7/7); 其中 4 件落在 78 靶子内且是硬缺陷 (见 iss356_netlist_4rows_gnd_fix), 靶外 3 件只在 §2.2 登记 ③ KiCad 库计数实测 = 155 个 .pretty 目录 / 15,468 个 .kicad_mod 文件 ⇒ 与你的订正一致; 本单所有 lib:name 都逐个 test -f + md5 核过 (81 处) ④ 跨界 1 件: C_VBUS_GND 确实在主 PCB 板面 (2 land: GND / VBUS_5V_CHG) 而 BOM board 栏写镜框充电板 + dnp=DNP ⇒ 只登记事实, 留位/下板归老板; 另 C_VBUS_OUT 同属充电板 + DNP 但实测不在任何板面 ⇒ 不在多余 2 里; 多余 2 的第 2 件是 J_CHG (跨铰链界面) ⇒ 已登记在 HW/FP_TRUTH_BASELINE.md §4.3 与交卷页 §B5 K2',
         ref='HW/FP_TRUTH_BASELINE.md §4.3 · HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md §B1.2 §B5'),
]


def main():
    args = []
    for a in ARTIFACTS:
        args += ['--add-artifact', spec(**a)]
    for c in CLAIMS:
        args += ['--add-claim', spec(**c)]
    for n in NEEDS:
        args += ['--add-need', spec(**n)]
    for a in ANSWERS:
        args += ['--add-answer', spec(**a)]
    run(args)
    print('[driver] 已写入 state/fragments/hw.yaml (只经 state/frag_write.py)')


if __name__ == '__main__':
    main()
