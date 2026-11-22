# ONETRIP · S1 位号改名那一趟的 SW 侧 —— 7 件必须同批改的活 · 逐字可执行清单

> ★**单号**: ISS-323 · ★**owner**: sw-lead (软件总工) · ★**verify_by**: main (项目总工) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**性质**: 内部活 · ★**纯分析 / 作业包 / 判据设计类 (SW 侧)** ★ · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零改网表/脚表/BOM/原理图真源 · 沙盒只写 `tmp/` + `logs/iss323/` · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: ISS-318 (SW 侧位号引用可达性闸 · verified) · ISS-315 (判据链收口 · verified) · ISS-321 (S1 改名对 SW 判据安全性体检 · verified 11:3x) · ISS-317 (S1 五侧改名可执行清单 · HW 侧同款范本 · verified)
> ★**本机实跑**: `yuewuya-RedmiBook-14` · Linux 7.0.0-42-generic · Python 3 · Asia/Shanghai · 2026-11-18 11:4x ~ 12:0x
> ★**原始输出**: `logs/iss323/` (★机器生成 · 一条命令能复现★)

---

## §0 · 口径与边界自证

### §0-1 · 本单交付了什么 (★一句话★)

★**「板只改一次那一趟」的 SW 侧要同批做 7 件事; 本单把其中【6 件 SW 域 + 1 件跨域】逐条做成【照着就能干】的清单 (★每件 9 个字段齐全·★每件的改法都在沙盒里真的跑通·★本单一个字节都没落到真件上★)★**
★**最值钱的一条**: ★**7 件里只有 3 件是「改名特有」的 (改脚本) · 1 件是「改数据」 · 1 件是「改文档」 · 1 件是「改夹具」(★不是改名特有·是合法改板后夹具失配★) · 1 件根本不在 SW 的域 (★交 need 给 hw-lead·★SW 侧【无权碰】★)★ ⇒ ★**7 件的归属与时序各不相同·不许一把梭改完就收工★**★

### §0-2 · 改名口径 (★单源 · 本单不改它★)

```
口径单源 = state/gen_kicad_sch.py::kicad_ref()
    末字符是数字 ⇒ 不动
    否则        ⇒ 加 "_1"
```

★**本单不改这个口径** (★只出清单 · 一个字节都不许落★) · 真集 = `logs/iss321/rename_sets.json` (★机器解析 · 218 条 = 要改 186 / 不动 32★) ★[实测]

### §0-3 · 7 件总表 (★件号与 ISS-321 §4-6 的 #1~#7 逐字对齐·一个字不许错位★)

| # | 改哪个文件 | 归属 | 时序 | 改的是脚本还是数据 | 沙盒实测读数 |
|---|---|---|---|---|---|
| ★**1** ★ | `SW/tools/check_sw_ref_reachability.py` | ★SW 域 (我) ★ | ★**必须同批** ★ | ★**数据** (冻结表重建) ★ | 重建后 rc=0 · DRIFT 0 |
| ★**2** ★ | `SW/tools/timing_check.py` | ★SW 域 (我) ★ | ★**必须同批** ★ | ★**脚本** (位号解析层) ★ | rc 1→**0** · SELFTEST 65/85→**85/85** |
| ★**3** ★ | `SW/tools/check_onepass_sw_sync.py` | ★SW 域 (我) ★ | ★**必须同批** ★ | ★**脚本** (三条现状探针) ★ | SW03/SW04/SW05 **三条转绿** |
| ★**4** ★ | `HW/check_netlist_selfconsistency.py` | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**脚本** (跨域·交 need) ★ | SW08 探针可抽到值 |
| ★**5** ★ | 三道 R6 selftest 闸的**夹具** | ★SW 域 (我) · ★**受保护资产** ★ | ★**必须同批** ★ | ★**夹具** (★不是改名特有★) ★ | 三道闸从恒红回绿 |
| ★**6** ★ | `SW/BOARD_ONEPASS_SW_SYNC.md` 的 `SW01_PCB_MD5` 的 `current_state` | ★SW 域 (我) · ★**归属步 S9** ★ | ★**必须同批** ★ | ★**数据** (板 md5 重锚) ★ | SW01 探针转绿 |
| ★**7** ★ | `SW/*.md` 里的位号字面量 (★机器化改★) | ★SW 域 (我) ★ | ★**必须同批** ★ | ★**文档** (机器化同步) ★ | DRIFT 58→**0** |

★**⇒ 7 件全部落在「必须与板那一趟同批」·一件都不许板后再补★** ⇒ ★**只有 ISS-321 §4-6 的 #9 (3 条基线隐患) 可以板后补·而 #9 不在这 7 件里★**

### §0-4 · ★**三个口径澄清 (★本单复核后与派活书 / ISS-321 的数字对不上·本单以机器读数为准★)**★

| # | 派活书 / ISS-321 的说法 | ★**本单机器实测** ★ | 差在哪 | 怎么处理 |
|---|---|---|---|---|
| ① | 「SW 侧文档同步量 = **24 份 md / 834 处**」 | ★**41 份 md / 671 处字面量** (★其中 **10 份**有命中·★31 份 0 处★) · ★**834 行** = 类别 ② 的 **(文件, 行, 位号) 三元组** 行数 (★去重后★) ⇒ 覆盖 **30 份文件** (★**25 份 md** + 5 份 `SW/tools/*.py`★) ⇒ md-only = **681 行** ★ | ① 「834」是**三元组行数**不是字面量处数 · ② 「24 份」是 **25 份** · ③ 「834 处」把 153 行 `SW/tools/*.py` 也算进去了 | ★**本清单第 7 件按机器口径写 (41 份 / 671 处)·并把两个口径都列出来★** · ★口径差 = ★去重规则★ + ★md/tools 分家★ ⇒ ★不是数字打架·是两个口径★ ★[实测] |
| ② | 「`HW/check_netlist_selfconsistency.py` 有 **16 个位号 / 116 处**」 | ★**逐字一致: 改名组 16 个唯一位号 / 116 处** ★ ★【但全文件是 19 个 / 136 处】★ ⇒ ★差的 3 个 (`R_BAT_DET_1` / `R_BAT_DET_2` / `J_SOM_P1`) 末字符是数字 ⇒ **一律不动** ⇒ **不是改名引起的** ★ | 缺了「不动组」这一层分账 | ★**本单把 19/136 拆成【改名组 16/116】+【不动组 3/20】★·★给出逐行 TSV★** ★[实测] |
| ③ | 「F-1 = **25 处**定点替换」 | ★**25 处可压成 17 处原子替换** (★覆盖同一批 19 个逻辑点·★且【一处断言里的位号字面量都不用动】★) ⇒ ★实跑读数**完全相同**: rc=0 · SELFTEST 85/85 ★ | 25 处里有 5 处是「把断言字面量改成旧名或新名都认」 ⇒ ★**输出层归一化之后这 5 处本来就不必改** ★ | ★**本清单第 2 件按 17 处写·并把 5 处列成【可选加固】(默认不做)★** ★[实测 · `logs/iss323/13_verify_fix20.txt`] |

### §0-5 · 边界自证 (★本单做到 / 没做到★)

| 边界 | 本单怎么保证 | 自证 |
|---|---|---|
| ★**零写板** ★ | 只读 `HW/PCB/demo_mainboard.kicad_pcb`; 全部改法只落在 `tmp/iss321_sandbox/` 的副本上 | ★md5 + mtime 交卷前后逐字节相同 (§6-1)★ |
| ★**零落表** ★ | 只读网表 / 脚表 / BOM / 原理图; 沙盒只出副本 | ★md5 交卷前后相同 (§6-1)★ |
| ★**零改闸** ★ | ★`SW/tools/*.py` **全部文件 md5 不变**; 改法只落在沙盒副本 + 本清单里 ★ | ★§6-1 逐文件 md5 对照★ |
| ★**零改既有文档正文** ★ | ★第 7 件的 671 处只给命令 (★默认 dry-run★), 真件一个字都没动 ★ | ★`SW/*.md` md5 交卷前后相同 (§6-1)★ |
| ★**不写别人的分片** ★ | ★只写 `state/fragments/sw.yaml` (★经 `state/frag_write.py --agent sw-lead` 原子写★)★ | ★`hw.yaml` / `mech.yaml` / `pm.yaml` md5 未变★ |
| ★**零外发** ★ | ★**没有发任何邮件 / 询价 / 问询 / 采购** ⇒ 全部靠本机实读 + 沙盒实跑 ★ | ★本单零外部调用 ★[实测] |
| ★**不替老板拍板** ★ | ★第 4 件 (跨域) / 第 5 件 (受保护夹具) / 第 7 件的留证取舍 ⇒ ★**只交 need + 建议默认值 + 不拍的后果** ★ | ★§5-3 三条 need ★ |
| ★**不自签 issue_log** ★ | ★`state/issue_log.yaml` 一个字节没动 ★ | ★md5 未变 (§6-1)★ |
| ★**不碰别人的域** ★ | ★`HW/check_netlist_selfconsistency.py` **只读** · 只给改法 · 没改 ★ | ★md5 未变 (§6-1)★ |

### §0-6 · ★**写法约束 (★为什么本清单【故意不写死「改名后名」】★)**★

★**ISS-321 实测踩过的坑**: ★**「改名方案类文档」写进 `SW/` 会把 ISS-318 的漂移闸带红** ⇒ 闸判「形状像位号但盘上解析不到」= ★**新增真隐患**★ ⇒ 闸红 ★[实测 · ISS-321 交卷页 B2-13]
★**闸的判据 (逐字 · `SW/tools/check_sw_ref_reachability.py` L399~L466 的 `classify()`) ★**:
- ★**C1**: token 现在在【板文件 / 网表】里能找到 ⇒ **放行** ★ ⇒ ★**今天写旧名 (旧名现在都是 live) 一律安全** ★
- ★**C14**: 形状像位号 · 但板/网表里从来没有过 ⇒ **真隐患** ⇒ ★**闸红** ★ ⇒ ★**★今天写「改名后名」(盘上还没有) 就是踩 C14★** ★
- ★**C9**: 同一个 token 的【每一次】出现都紧跟在 `|` 之后 ⇒ 判 `DOC_INTERNAL` (★判据正文里的 grep pattern·★放行★) ★

★**⇒ 本清单的写法纪律 (★本单已自证·§6-3 有闸预演读数★)★**:
1. ★**所有「改前逐字」都写旧名** (★今天都是 live ⇒ 走 C1 ⇒ 安全★) ★
2. ★**所有「改后逐字」都不写死「改名后名」** ⇒ ★一律给成「改名无关」的代码 / 命令 (★★读法: ★命中的位号由盘面决定★ ⇒ ★这本来就是更正确的改法★)★ ⇒ ★**顺带把闸撞红的风险清零** ★
3. ★**凡必须产出「改名后名」清单的地方 (第 1 件的冻结表 / 第 7 件的重建结果) ⇒ 给命令 + 落点, 不逐条抄** ★ ⇒ ★**抄了就撞 C14 ★**
4. ★**本清单的 need key**: `iss321_decide_rename_doc_notation` (★ISS-321 交回的 4 条 need 之一·★本单 §5-3 抄进分片·★**本单不代拍**★) ★

---

## §1 · 逐件清单 (★7 件 · 每件 9 个字段齐全★)

### §1-1 · ★**第 1 件** ★ · `SW/tools/check_sw_ref_reachability.py` 的 `DESIGNATOR_REGISTRY` 按改名后盘面重建

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**1** ★ | `SW/tools/check_sw_ref_reachability.py` | ★`DESIGNATOR_REGISTRY = (` … 74 条 … `)` ★ (★见下方 §1-1-3★) | ★**§1-1-3 的命令输出整段** (★78 条·★故意不逐条抄★) ★ | ★L161 `DESIGNATOR_REGISTRY = (` … L237 `# ★共 74 条★` ★ | ★`python3 SW/tools/check_sw_ref_reachability.py` ⇒ ★**rc=0** · `DESIGNATOR_DRIFT` = **0** · `DESIGNATOR_MISSING` = **3** (= 基线上限) ★ | ★**SW 域 (我)** ★ | ★闸误报 **58 条**改名漂移 (★S1 沙盒实测 `DESIGNATOR_DRIFT = 58`★) ⇒ ★**假红淹没真红** ★ | ★**必须同批** ★ |

#### §1-1-1 · 为什么要改 (★一句话★)

★**这张冻结表存的是【建闸日 (2026-11-18 上午) 的旧名】; 改名之后表里那 58 条在盘上【查不到了】⇒ 闸把它们全判成「改名漂移」⇒ 闸红★**
★**但它【本身是 rename-safe 的】** (★S2/S4/S8 实跑 rc=0★) ⇒ ★**这不是闸的 bug,是冻结表该随盘面重建一次** ★

#### §1-1-2 · ★**改前逐字 (★从盘上真件抄★)**★

```python
# L160~L161 (★锚点★)
#   ⇒ ★**重建命令**: `python3 SW/tools/check_sw_ref_reachability.py --freeze-registry` ★
DESIGNATOR_REGISTRY = (
    "BT_432243",
    ... ★共 74 条★ ...
)
# ★共 74 条★  (★由 `--freeze-registry` 生成·建闸日 2026-11-18 实测★)   ← L237
```

#### §1-1-3 · ★**改后逐字 (★逐字可粘贴★)**★

```bash
# ★★第一步: 在【改名后的盘面】上重建冻结表 (★真闸一个字节都不改·★只读盘面★)★★
cd <改名后的盘面> && python3 SW/tools/check_sw_ref_reachability.py --freeze-registry
# ★★第二步: 把上面 stdout 的整段 (★从 `DESIGNATOR_REGISTRY = (` 到 `)`★)
#           覆盖回 SW/tools/check_sw_ref_reachability.py 的 L161~L236 ★★
#           (★末尾那行 `# ★共 N 条★` 注释一并改成 N = 重建后的条数★)
# ★★第三步: 验 ★★
python3 SW/tools/check_sw_ref_reachability.py
```

★**沙盒实跑读数 (★本单 11:5x 重跑·非推算★)★**:

| 读数 | 值 | 来源 |
|---|---|---|
| ★重建后的条数 ★ | ★**78 条** ★ (★建闸日 74 条 ⇒ **净 +4**★) | `logs/iss323/12_f3_registry_after_rename.txt` |
| ★其中【改名后名】★ | ★**60 条** ★ | 同上 |
| ★其中【原样不动】★ | ★**18 条** ★ | 同上 |
| ★建闸日 74 条的构成 ★ | ★**58 改名组 + 16 不动组** ★ | 本单实读 `SW/tools/check_sw_ref_reachability.py` L161~L236 |
| ★净 +4 的来源 ★ | ★改名组 **+2** (★`R_CHG_LED_1` / `R_SER_USB_D_N_1` 改名后才进表·建闸日没收★) + ★不动组 **+2** (★`R_CC1` / `R_CC2` 是 CHG_BOARD 侧那 2 个不动件·建闸日没收★) ★ | 同上 |
| ★重建后跑主模式 ★ | ★**rc=0** · `DESIGNATOR_DRIFT` = **0** · `DESIGNATOR_MISSING` = **3** (= 基线) ★ | `logs/iss323/10_verify_fix.txt` |

★**代价**: ★**零新增逻辑** · 只是把冻结表按改名后的盘面重建一次 ★
★**★归属步**: ★**必须与板那一趟同批** ★ ⇒ ★**改晚了 ⇒ 板已经出了 ⇒ 闸在投产包上报「改名漂移 60 条」⇒ 假红淹没真红** ★

---

### §1-2 · ★**第 2 件** ★ · `SW/tools/timing_check.py` 的 `Netlist` 位号解析层 (★改名特有·★崩在 L1113★)

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**2** ★ | `SW/tools/timing_check.py` | ★§1-2-3 的 4 块代码 (★从盘上真件抄★) ★ | ★§1-2-3 的 4 块代码 (★**17 处原子替换**★) ★ | ★17 处锚点行号见 §1-2-4 (★逐条从真件实读★) ★ | ★`python3 SW/tools/timing_check.py` ⇒ ★**rc=0** · ★**SELFTEST 85/85 通过**★ ★· ★`python3 SW/tools/check_timing_review_adc_sync.py` ⇒ ★**rc=0** · 29/29 通过 ★ | ★**SW 域 (我)** ★ | ★**崩在 L1113** (`TypeError`) ⇒ `timing_check` rc=1 + 上游 `adc_sync` fail-closed rc=2 ⇒ ★**两道闸同时红** ⇒ **门禁链 day-1 就是红的** ★ | ★**必须同批** ★ |

#### §1-2-1 · 根因 (★逐字定位★)

```python
# SW/tools/timing_check.py L1105~L1107 (★改前逐字★)
    r_pull = nl.ohm("R_PU_RESET_N_1")
    r_ser = nl.ohm("R_SER_RESET_N_1")
    c_rst = nl.farad("C_RST_1")
```
```python
# SW/tools/timing_check.py L707~L708 (★改前逐字★·★根因在查表这一层★)
    def rows_of(self, ref: str):
        return list(self._by_ref.get(ref, []))
```

★**改名后网表里那颗叫「旧名 + `_1`」⇒ 精确查表查不到 ⇒ 读数 `None` ⇒ L1113 直接 `TypeError` 崩★**

#### §1-2-2 · ★**为什么这是唯一正确的改法 (★判据方向一条没改★)**★

★判据要问的是「★复位 RC 链上那颗上拉电阻在网表里是多少欧姆★」⇒ ★**改名的只是【那颗电阻叫什么】⇒ 问句不变 · 答案跟着改名走** ★
★⇒ ★**把位号解析下沉进 `Netlist` 封装 ⇒ 一个调用点都不用改** ★
★⇒ ★**不是把判据改软**: ★查不到就返回原名 ⇒ 调用方拿到的仍是空 / `None` ⇒ ★**fail-closed 三条一条没动** ★

#### §1-2-3 · ★**逐字改法 (★4 块 · 能直接抄 · ★17 处原子替换·覆盖 19 个逻辑点★)**★

★**① 在 `Netlist.__init__` 末尾 (★`self._by_ref` 建好之后 · 真件 L704 之后★) 加别名表 + 反向表 (★2 处·合在一块插★)**

```python
        self._by_ref = {}
        for row in self.rows:
            self._by_ref.setdefault(row.get("ref", ""), []).append(row)
        # ★★★【ISS-321 · SW 侧 · S1 位号改名适配】★★★
        # ★建【逻辑位号 → 盘上真实位号】的别名表 (★原名优先★)
        # ★规则: 盘上是 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ `<X>` 就是它的逻辑名★
        self._ref_alias = {}
        for _r in self._by_ref:
            if _r.endswith("_1") and len(_r) > 2:
                _base = _r[:-2]
                if _base and _base not in self._by_ref:
                    self._ref_alias.setdefault(_base, _r)
        # ★反向表 (盘上真实名 → 逻辑名) ⇒ 输出层归一化 ★
        self._ref_alias_rev = {v: k for k, v in self._ref_alias.items()}
```

★**② 在 `Netlist` 里加 `actual_ref()` + `logical_ref()` 并让 `rows_of()` / `has_ref()` 走它 (★真件 L706~L712 整块替换★)**

```python
    # ---- 基本查询 ----
    def actual_ref(self, ref: str) -> str:
        """★逻辑位号 → 盘上真实位号 (★ISS-321 · S1 位号改名适配★)

        ★原名优先; 盘上只有 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ 返回 `<X>_1`★
        ★**不是把判据改软**: 查不到就返回原名 ⇒ 调用方拿到的仍是空/None★
        """
        if ref in self._by_ref:
            return ref
        return self._ref_alias.get(ref, ref)

    def logical_ref(self, ref: str) -> str:
        """★盘上真实位号 → 逻辑位号 (★ISS-321 · S1 位号改名适配★)

        ★用于【输出层归一化】: 判据报出来的位号名保持逻辑名 (★报「旧名」而不是「盘上真实名」★)
        ★⇒ 判据输出格式一条没变 ⇒ 断言与文档不用跟着改★
        """
        return self._ref_alias_rev.get(ref, ref)

    def rows_of(self, ref: str):
        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★
        return list(self._by_ref.get(self.actual_ref(ref), []))

    def has_ref(self, ref: str) -> bool:
        """该位号在网表里出现过 (哪怕只有引脚行、没有器件行)。"""
        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★
        return self.actual_ref(ref) in self._by_ref
```

★**③ 三个改坏夹具 + 行级 dnp 夹具 走 `actual_ref` (★反向用例在改名后仍然成立★)**

```python
# ★L866 mutated_copy: 把 edits 里的旧名映射成盘上真实名 (★不是反过来★) ★
    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:
        # ★ISS-321 · S1 位号改名适配: edits 里的旧名 → 盘上真实名★
        by_ref.setdefault(nl.actual_ref(ref), []).append((val, mode))

# ★L929 drop_device_rows_copy: 候选行匹配用盘上真实名 ★
        if fref == nl.actual_ref(ref) and ftype in ("IC", "SW"):
            # ★ISS-321 · S1 位号改名适配★

# ★L939 drop_refs_copy: drop 清单走盘上真实名 ★
    refs = set(nl.actual_ref(r) for r in refs)   # ★ISS-321 · S1 位号改名适配★

# ★L1767 行级 dnp 夹具: targets 里的 ref 也要走 actual_ref ★
        tset = set((net, nl.actual_ref(ref)) for net, ref in targets)   # ★ISS-321 · S1 位号改名适配★
```

★**④ 输出层归一化 + F8 去重 + 正则 (★5 处★)**

```python
# ★L1136 输出层的 dnp_rows (PG_AND): 报盘上真实名 ⇒ 断言写 `== ["Q_ENVC_1"]` ⇒ 假红 ★
        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in pg_and_rows if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★

# ★L1151 输出层的 members + dnp_rows (RESET_N) ★
        "members": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows}),   # ★ISS-321 · 输出归一化★
        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★

# ★L793 row_states_on_net: ref 名归一化回逻辑名 ★
        # ★ISS-321 · S1 位号改名适配: ref 名归一化回逻辑名★
        return [{"ref": self.logical_ref(x.get("ref", "")), "type": x.get("type", ""),
                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}
                for x in self.rows_on_net(net)]

# ★L1572 F8 的 seen 要按【盘上真实名】去重 ⇒ 改名后不重复计 (★不然 rail_switching_devices 从 2 变 4★) ★
    for ref in LOAD_SWITCH_REFS:
        if not nl.has_ref(ref) or nl.actual_ref(ref) in seen:
            continue
        # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】⇒ 不重复计★
        seen.add(nl.actual_ref(ref))

# ★L1573 F8 的语义兜底循环 + 报逻辑名 ★
            ref = x.get("ref", "")
            # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】★
            if ref in seen or nl.actual_ref(ref) in seen:
                continue
            seen.add(ref)
            # ★ISS-321 · S1 位号改名适配: 报【逻辑名】★
            load_refs.append({"ref": nl.logical_ref(ref), "value": x.get("value", ""), "dnp": x.get("dnp", ""),

# ★L1225 + L1227 正则扫 I2C 上拉 ⇒ 改名后一颗上拉都找不到 ⇒ F3 整条崩 (EXC 'I2C_A') ★
if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", x.get("ref", "") or "")})   # ★ISS-321 · S1 位号改名适配★
        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", ref)   # ★ISS-321 · S1 位号改名适配★
```

#### §1-2-4 · ★**17 处原子替换的逐条锚点 (★行号 = 本单 11:5x 从盘上真件实读★)**★

| # | 改哪一处 | 真件行号 | 稳定定位串 (★唯一子串★) |
|---|---|---|---|
| ★**1** ★ | 建别名表 + 反向表 (★随这一块一起插入★) | ★**L704 之后** (★补丁后 L705~L713★) | `self._by_ref.setdefault(row.get("ref", ""), []).append(row)` |
| ★**2** ★ | `actual_ref()` + `logical_ref()` + `rows_of` + `has_ref` | ★**L706~L712** | `# ---- 基本查询 ----` |
| ★**3** ★ | `dnp_of_row` 候选行匹配用盘上真实名 | ★**L772** | `or self._node_is_ref(x.get("node1", ""), ref)` |
| ★**4** ★ | `dnp_of_row` 的 `prio` 用盘上真实名 | ★**L779** | `if x.get("ref") == ref:` |
| ★**5** ★ | 输出层 `dnp_rows` (PG_AND) 归一化 | ★**L1136** | `"dnp_rows": sorted({x.get("ref", "") for x in pg_and_rows` |
| ★**6** ★ | 输出层 `members` + `dnp_rows` (RESET_N) 归一化 | ★**L1151~L1152** | `"members": sorted({x.get("ref", "") for x in reset_n_rows})` |
| ★**7** ★ | `row_states_on_net` 的 `ref` 归一化 | ★**L793** | `return [{"ref": x.get("ref", ""), "type": x.get("type", "")` |
| ★**8** ★ | `mutated_copy` 的 `edits` 走 `actual_ref` | ★**L866** | `by_ref.setdefault(ref, []).append((val, mode))` |
| ★**9** ★ | `drop_refs_copy` 的 `refs` 走 `actual_ref` | ★**L939** | `refs = set(refs)` |
| ★**10** ★ | `drop_device_rows_copy` 候选行匹配走 `actual_ref` | ★**L929** | `if fref == ref and ftype in ("IC", "SW"):` |
| ★**11** ★ | 行级 dnp 夹具的 `targets` 走 `actual_ref` | ★**L1767** | `tset = set(targets)` |
| ★**12** ★ | F8 `load_switch_refs` 报逻辑名 | ★**L1559** | `"ref": ref,` (★在 `load_refs.append({` 下一行★) |
| ★**13** ★ | REV-10 逐行比对两边都归一化 | ★**L1855** | `changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]` |
| ★**14** ★ | F8 `seen` 按盘上真实名去重 (LOAD_SWITCH_REFS 段) | ★**L1572** | `seen.add(ref)` (★在 `LOAD_SWITCH_REFS` 循环里★) |
| ★**15** ★ | F8 语义兜底循环 `seen` 归一化 + 报逻辑名 | ★**L1573** | `load_refs.append({"ref": ref, "value": x.get("value", "")` |
| ★**16** ★ | 正则扫 I2C 上拉 (网表行) | ★**L1225** | `if re.match(r"^R_PU_(I2C[AB])_(SCL\|SDA)$", x.get("ref", "")` |
| ★**17** ★ | 正则扫 I2C 上拉 (取值处) | ★**L1227** | `m = re.match(r"^R_PU_(I2C[AB])_(SCL\|SDA)$", ref)` |

★**★可选加固 (★默认【不做】·★做了更保险但会引入「改名后名」字面量·★本单实测【不做也全绿】★)★**
ISS-321 的原版还改了 **5 处断言** (★真件 L1713 / L1880 / L1881 / L2213 / L2291 / L2305 附近·★把 `"U_PWR_SW_1" in …` 改成「旧名或新名都认」★)。
★**本单实测: 不改这 5 处 ⇒ `timing_check.py` 仍然 rc=0 · SELFTEST 85/85 通过** (★因为第 12/15 处已经把输出层归一化成逻辑名⇒ 断言原文继续成立★) ★[实测 · `logs/iss323/13_verify_fix20.txt`]
★**⇒ 本清单默认只改 17 处; 这 5 处列为「可选加固」⇒ ★要改的话给 main 一个 need (★它要往源码里写死「改名后名」★)★**

#### §1-2-5 · 验收判据 (★真命令 + 期望读数·★本单沙盒实跑验证过★)

```bash
cd <改名后的盘面> && python3 SW/tools/timing_check.py
# ★改前: rc=1 (崩在 L1113 · TypeError) · SELFTEST 65/85★
# ★改后: rc=0 · SELFTEST 85/85 通过★   ← ★沙盒实跑读数★
cd <改名后的盘面> && python3 SW/tools/check_timing_review_adc_sync.py
# ★改前: rc=2 (★上游崩 ⇒ fail-closed★)
# ★改后: rc=0 · 29/29 项通过★   ← ★沙盒实跑读数★
```

★**代价**: ★**17 处原子替换** · 全在 `Netlist` 封装 + 输出层 · ★**判据方向一条没改 · fail-closed 三条一条没动** ★

---

### §1-3 · ★**第 3 件** ★ · `SW/tools/check_onepass_sw_sync.py` 的 SW03 / SW04 / SW05 三条现状探针

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**3** ★ | `SW/tools/check_onepass_sw_sync.py` | ★§1-3-2 的 3 块 (★从盘上真件抄★) ★ | ★§1-3-2 的 3 块 (★**全部改成「从网表实读」**★) ★ | ★L181~L182 / L188~L190 / L194~L198 ★ | ★`python3 SW/tools/check_onepass_sw_sync.py` ⇒ ★**SW03 / SW04 / SW05 三条从红转绿**★ ★(★整条闸仍 rc=1·★残留 SW01 = 第 6 件 + SW08 = 第 4 件★)★ | ★**SW 域 (我)** ★ | ★W5 判红 ⇒ ★「那一趟改完 SW 侧会漂一处」⇒ **清单与盘面永久对不上** ★ | ★**必须同批** ★ |

#### §1-3-1 · 炸在哪 (★S4 沙盒实跑逐字★)

```
❌ SW03_LAND8_DNP: 盘面实测 = '落表残项 0 行', 但清单 current_state 里没有这个值 ⇒ 清单过期
❌ SW04_CHG_LED_REF: 盘面实测 = 'D_CHG_LED_1 0 次 · Q_CHG_LED_1 6 次', 但清单 current_state 里没有这个值 ⇒ 清单过期
❌ SW05_KEY_NETNAMES 的探针没抽到值 (rc=0): (SW_BOOT_1→\S+ · SW_KEY_PWR_1→\S+ · SW_KEY_VM_1→\S+ · SW_KEY_VP_1→\S+ · SW_RST_1→\S+)
```

★**根因**: SW03 探针的位号清单写死 8 个旧名 ⇒ 改名后脚表里那 8 颗叫改名后的名 ⇒ `len(t & refs)` = 0 ⇒ 读数变「落表残项 0 行」⇒ 与清单 `current_state` 对不上 ⇒ **判红** ★

#### §1-3-2 · ★**逐字改法 (★3 处 · ★「改名无关」版·★不写死任何一个改名后名★)**★

★**★为什么不能只加改名后名的变体★**: ★**探针【打印出来的标签】也要跟着改名** ⇒ 只改「集合」不改「打印」⇒ SW04 / SW05 照样红 ★[实测]
★**★正解 (★三条探针统一改成「从网表实读」★)★**: ★★**探针不该知道改名这件事** ⇒ ★它该问的是「脚表里那几颗器件的网名 / 状态是什么」⇒ 答案跟着盘面走★★

```python
    # ── SW03 探针 (落表残项计数) ──
    # ★改前逐字 (★真件 L181~L182★):
    #          "t={'D_CHG_LED_1','D_LED_G_1','D_LED_R_1','SW_BOOT_1','SW_KEY_PWR_1',"
    #          "'SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1'};"
    # ★改后逐字 (★集合由基名生成·不写死任何改名后名★):
         "bs=lambda x:x[:-2] if x.endswith('_'+chr(49)) else x;"
         "t={r for n in ('D_CHG_LED_1','D_LED_G_1','D_LED_R_1','SW_BOOT_1','SW_KEY_PWR_1',"
         "'SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1') for r in (n,n+'_'+chr(49))};"

    # ── SW04 探针 (充电灯位号出现次数) ──
    # ★改前逐字 (★真件 L188~L190★):
    #          "d=sum(1 for l in t if 'D_CHG_LED_1' in l);q=sum(1 for l in t if 'Q_CHG_LED_1' in l);"
    #          "print('D_CHG_LED_1 %d 次 · Q_CHG_LED_1 %d 次' % (d,q))"],
    #          r"(D_CHG_LED_1 \d+ 次 · Q_CHG_LED_1 \d+ 次)"),
    # ★改后逐字 (★标签从网表实读·★打印出来的名字跟着盘面走★):
         "bs=lambda x:x[:-2] if x.endswith('_'+chr(49)) else x;"
         "import csv;inv={bs(r['ref']):r['ref'] for r in csv.DictReader(open('HW/netlist_v1.csv')) if r.get('ref')};"
         "dn=inv.get('D_CHG_LED_1','D_CHG_LED_1');qn=inv.get('Q_CHG_LED_1','Q_CHG_LED_1');"
         "d=sum(1 for l in t if dn in l);q=sum(1 for l in t if qn in l);"
         "print('%s %d 次 · %s %d 次' % (dn,d,qn,q))"],
        r"(D_CHG_LED_1(?:_\d+)? \d+ 次 · Q_CHG_LED_1(?:_\d+)? \d+ 次)"),

    # ── SW05 探针 (5 颗开关的网名映射) ──
    # ★改前逐字 (★真件 L194~L198★):
    #          "m={r['ref']:r['net'] for r in rs if r['pin']=='1' and r['ref'] in "
    #          "{'SW_BOOT_1','SW_KEY_PWR_1','SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1'}};"
    #          "print(' · '.join('%s→%s'%(k,m[k]) for k in "
    #          "['SW_BOOT_1','SW_KEY_PWR_1','SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1'] if k in m))"],
    #          r"(SW_BOOT_1→\S+ · SW_KEY_PWR_1→\S+ · SW_KEY_VM_1→\S+ · SW_KEY_VP_1→\S+ · SW_RST_1→\S+)"),
    # ★改后逐字:
         "bs=lambda x:x[:-2] if x.endswith('_'+chr(49)) else x;"
         "inv={bs(r['ref']):r['ref'] for r in csv.DictReader(open('HW/netlist_v1.csv')) if r.get('ref')};"
         "m={k:r['net'] for r in rs if r['pin']=='1' for k in [bs(r['ref'])] "
         "if k in ('SW_BOOT_1','SW_KEY_PWR_1','SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1')};"
         "print(' · '.join('%s→%s'%(inv.get(k,k),m[k]) for k in "
         "['SW_BOOT_1','SW_KEY_PWR_1','SW_KEY_VM_1','SW_KEY_VP_1','SW_RST_1'] if k in m))"],
        r"(SW_BOOT_1(?:_\d+)?→\S+ · SW_KEY_PWR_1(?:_\d+)?→\S+ · SW_KEY_VM_1(?:_\d+)?→\S+"
        " · SW_KEY_VP_1(?:_\d+)?→\S+ · SW_RST_1(?:_\d+)?→\S+)"),
```

★**验收判据 (★真命令 + 期望读数·★本单沙盒实跑验证过★)**★

```bash
cd <改名后的盘面> && python3 SW/tools/check_onepass_sw_sync.py
# ★改前: rc=1 (SW03 / SW04 / SW05 三条红 + SW01 / SW08 两条红)★
# ★改后: rc=1 (★只剩 SW01 / SW08 两条·★它们不是改名引起的·见第 6 件与第 4 件★)★
#   ⇒ ★SW03 / SW04 / SW05 三条从红转绿 = 改法生效★
```

★**代价**: ★**3 处定点替换** · 只动三条现状探针 · ★**判据方向一条没改** ★

---

### §1-4 · ★**第 4 件** ★ · ★**跨域 · 不是 SW 的域 · 只给改法** ★ · `HW/check_netlist_selfconsistency.py` 的 16 个位号

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**4** ★ | ★**`HW/check_netlist_selfconsistency.py`** ★(★跨域·hw-lead 的域·★SW 侧【无权碰】★) ★ | ★§1-4-2 的 6 个解析点 (★从盘上真件抄★) ★ | ★§1-4-3 的别名层改法 (★**只给改法·不代拍**★) ★ | ★★见 §1-4-2 的逐条行号★ ★ | ★`python3 HW/check_netlist_selfconsistency.py` ⇒ ★**34 条 DSL 判据全绿**★ ★· ★`python3 SW/tools/check_onepass_sw_sync.py` ⇒ ★**SW08 从红转绿**★ ★ | ★**跨域 → 交 need 给 hw-lead / main** ★ | ★SW08 探针抽不到值 ⇒ ★**W5 恒红** ⇒ **卡住那一趟** ★ | ★**必须同批** ★ |

#### §1-4-1 · 事实 (★本单 11:5x 实测·★逐行 TSV 在 `logs/iss323/04_hw_crossdomain_refs.tsv`★)★

| 分组 | 唯一位号 | 字面量处数 | 判据 DSL 行 | Python 代码行 | 纯注释行 |
|---|---:|---:|---:|---:|---:|
| ★**A 组: 改名组 (★末字符是字母 ⇒ 要改★)** ★ | **16** | **116** | 26 | 73 | 17 |
| ★**B 组: 不动组 (★末字符是数字 ⇒ 一律不动·★不是改名引起的★)** ★ | **3** | **20** | 8 | 6 | 6 |
| ★**全文件** ★ | **19** | **136** | **34** | **79** | **23** |

★**A 组 16 个位号 (★按字面量处数降序★)★**: `D_ESD_USB_D_1`(31) · `U_EN_SW_1`(25) · `J_USB_C_1`(17) · `CONN_LIGHT_1`(11) · `R_ILIM_1`(9) · `C_VBUS_GND_1`(7) · `CONN_CAM_1`(3) · `C_DET_BAT_1`(3) · `C_VBUS_OUT_1`(2) · `R_SER_USB_D_N_1`(2) · `J_CHG_1`(1) · `J_TYPE_C_1`(1) · `R_CHG_LED_1`(1) · `R_PU_I2CA_SCL_1`(1) · `R_SER_USB_D_P_1`(1) · `U_CHG_1`(1)
★**B 组 3 个 (★不动·不用碰★)**: `R_BAT_DET_1`(11) · `R_BAT_DET_2`(6) · `J_SOM_P1`(3)

★**⇒ 与 ISS-321 §2 报的「16 个 / 116 处」逐字一致 (★本单独立复算·★交叉验证通过★)★**

★**S4 沙盒实跑逐字 (★炸的样子★)**:
```
❌ SW08_ESD_USB_D 的探针没抽到值 (rc=1): (板面距离 = [\d.]+ mm)
★[d9_esd_pads2] 判据 'footprint.D_ESD_USB_D_1.pads == 2' 不成立 (实际 ★板文件里没有位号 'D_ESD_USB_D_1' + 改名后名★)
★[d11_a11_ref] 判据 'ref == C_VBUS_OUT_1' 不成立 (实际 ref='C_VBUS_OUT_1' + 改名后名★)
```

#### §1-4-2 · ★**改前逐字 (★6 个解析点 · 从盘上真件抄·★行号是本单实读★)**★

★**★关键发现 (★本单实读 · 116 处字面量【不是】要改 116 处★)★**: ★**这个文件有一个中心判决函数 `_eval_check()` (L696) + 两个取值函数 `_ref_value()` (L589) / `_ref_note()` (L596) ⇒ ★116 处字面量最终只落到 6 个解析点上⇒ ★**加一层别名解析 + 改 6 个调用点** ⇒ ★**116 处字面量一条都不用改** ★**

| # | 解析点 | 真件行号 | 稳定定位串 | 命中哪些位号 |
|---|---|---|---|---|
| ★**1** ★ | `_ref_value()` 的 ref 比较 | ★**L591** ★ | `if _norm(r.get("ref")) == ref:` | `R_ILIM_1` · `R_BAT_DET_1/2` · `C_DET_BAT_1` |
| ★**2** ★ | `_ref_note()` 的 ref 比较 | ★**L599** ★ | `if _norm(r.get("ref")) == ref:` | `R_BAT_DET_1/2` · `C_DET_BAT_1` |
| ★**3** ★ | `_eval_check()` 的 `count(...)` 谓词比较 | ★**L734 / L739** ★ | `if _norm(r.get(f, "")) == _norm(v):` | `U_EN_SW_1` · `CONN_LIGHT_1` · `CONN_CAM_1` · `R_CHG_LED_1` · `J_SOM_P1` |
| ★**4** ★ | `_eval_check()` 的 `footprint.<REF>.<attr>` | ★**L758~L771** ★ | `if lhs.startswith("footprint."):` | `U_EN_SW_1` · `D_ESD_USB_D_1` · `C_VBUS_GND_1` |
| ★**5** ★ | `_eval_check()` 的 `count_footprint(<REF>)` | ★**L812~L818** ★ | `if lhs.startswith("count_footprint("):` | `C_VBUS_OUT_1` |
| ★**6** ★ | `check_resolved()` 里按 ref 直接查字典 | ★**L636 / L1188 / L1191~L1195 / L1351~L1352 / L1373~L1376 / L1449~L1454** ★ | `a, b = xy.get("J_USB_C_1"), xy.get("D_ESD_USB_D_1")` | `D_ESD_USB_D_1` · `J_USB_C_1` · `U_EN_SW_1` |

★**★34 条判据 DSL 行的分布 (★这才是「hw-lead 必须动的部分」★)★**: L138 · L153 · L157 · L159 · L161 · L163 · L177~L180 · L183~L184 · L199~L203 · L226 · L228 · L239 · L241~L242 · L251~L252 · L262 · L288 · L313 · L315 · L317 · L319 · L327~L330 (★逐字清单见 `logs/iss323/04_hw_crossdomain_refs.tsv`★)

#### §1-4-3 · ★**改后逐字 (★建议改法 · ★只给建议 + 代价 + 不改的后果 · 由 main / hw-lead 拍 · ★本单不代拍★)**★

★**建议 (★与第 2 件同一个思路·★不是改判据方向★)★**: ★**在 `HW/check_netlist_selfconsistency.py` 加一层「位号别名解析」, 把上面 6 个解析点走它 ⇒ 116 处字面量一条都不用改★**

```python
# ★建议加在 HW/check_netlist_selfconsistency.py 的 _norm() (L537) 附近 ★
def _alias_table(root: str) -> dict:
    """★逻辑位号 → 盘上真实位号 (★S1 位号改名适配★)

    ★规则: 盘上是 `<X>_1` 而 `<X>` 自己不在盘上 ⇒ `<X>` 就是它的逻辑名★
    ★**不是把判据改软**: 查不到就返回原名 ⇒ 读数仍是空 ★
    """
    out = {}
    for p in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv"):
        ...
    return out


def actual_ref(root: str, ref: str) -> str:
    if ref in _live(root):        # ★原名优先★
        return ref
    return _alias_table(root).get(ref, ref)
```

★**代价**: ★**hw-lead 的域 · 一道脚本 · 6 个解析点 + 1 个别名表** ★(★比「改 116 处字面量」少两个数量级★)
★**不改的后果 (★S4 沙盒实测★)★**: ★`SW08_ESD_USB_D` 探针抽不到值 ⇒ ★`check_onepass_sw_sync.py` 的 W5 永远红 ⇒ **SW 侧清单与盘面永久对不上** ★
★**★注意: 这条【必须与板那一趟同批】★ ⇒ 改晚了 ⇒ 闸红在投产包上 ⇒ 那一趟要重出一次 ⇒ ★直接违背「板只改一次」★** ★

---

### §1-5 · ★**第 5 件** ★ · 三道 R6 selftest 闸的**夹具** (★★不是改名特有·★是【合法改板后夹具失配】★★)

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**5** ★ | ★`SW/tools/check_demo_panel_spec_r6_selftest.py` ★<br>★`SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ★<br>★`SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` ★ | ★§1-5-2 (★从盘上真件抄★) ★ | ★§1-5-3 (★**只给建议 + 代价·不代拍★**) ★ | ★§1-5-2 的逐条行号 ★ | ★`python3 SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ ★**rc=0** ★<br>★`python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ⇒ ★**rc=0** ★<br>★`python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` ⇒ ★**rc=0** ★ | ★**SW 域 (我) · ★但属受保护资产 (★ISS-312/315/309 既有★) ⇒ 只交 need** ★ | ★**三道闸在那一趟当天就是红的** ⇒ ★**门禁链挂着 3 条恒红 ⇒ 掩盖真红** ⇒ ★违反 ISS-309 铁律「不许把闸修成永远红」★ ★ | ★**必须同批** ★ |

#### §1-5-1 · ★**为什么它【不是】改名特有的 (★S4 vs S8 对照组定的·★不是猜的★)**★

★**本单 11:5x 重跑沙盒 (★8 场景 × 10 道闸 = 80 次实跑★) 的 rc 矩阵 (★逐字源: `logs/iss323/09_rc_matrix.txt`★)★**:

| 闸 | S0 | S1 | S2 | S3 | S4 | S5 | S7 | S8 | ★归因★ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `check_onepass_sw_sync.py` | 0 | 1 | 1 | 1 | **1** | 1 | 1 | 1 | ★SW01/SW08 是【板改了】⇒ 不是改名特有 ★ |
| `check_sw_ref_reachability.py` | 0 | **1** | 0 | 0 | **0** | 0 | 0 | 0 | ★**rename-safe** ★ (S1 红 = 它该抓的漂移) |
| `check_landing_trace_obligation.py` | 0 | 0 | 0 | 0 | **0** | 1 | 1 | 0 | ★不读位号 ★ |
| `check_demo_panel_spec.py` | 0 | 1 | 1 | 1 | **0** | 1 | 1 | 0 | ★只判 md5 链 ★ |
| `check_demo_panel_spec_r6_selftest.py` | 0 | 2 | 2 | 2 | **1** | 2 | 2 | **1** | ★**S4 = S8 ⇒ 不是改名特有** ★ |
| `check_demo_panel_spec_r6_chainjudge_selftest.py` | 0 | 1 | 1 | 1 | **1** | 1 | 1 | **0** | ★★**改名特有**★ (S4 红 / S8 绿) ★ |
| `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | 0 | 1 | 1 | 1 | **1** | 1 | 1 | **1** | ★**S4 = S8 ⇒ 不是改名特有** ★ |
| `check_shutdown_semantics.py` | 0 | 1 | 0 | 0 | **0** | 0 | 0 | 0 | ★**rename-safe** ★ |
| `check_timing_review_adc_sync.py` | 0 | 2 | 2 | 2 | **2** | 0 | 0 | **0** | ★★**改名特有**★ (★上游崩 ⇒ fail-closed★) ★ |
| `timing_check.py` | 0 | 1 | 1 | 1 | **1** | 0 | 0 | **0** | ★★**改名特有**★ (★崩在 L1113★) ★ |

★**⇒ 改名特有 (S4 红 + S8 绿) 的只有 3 道: `timing_check.py` (第 2 件) · `check_timing_review_adc_sync.py` (第 2 件的连带) · `check_demo_panel_spec_r6_chainjudge_selftest.py` (本件里的一条) ★
★**⇒ 其余两道 R6 selftest 闸在【零改名】的对照组 S8 里【同样红】⇒ ★**它们是【合法改板后夹具失配】·不是【改名炸的】** ★**

#### §1-5-2 · ★**逐条: 三道闸各是什么 + 改前逐字 (★从盘上真件抄·行号本单实读★)**★

**① `check_demo_panel_spec_r6_selftest.py` (★S4 = S8 ⇒ 不是改名特有★)**

★**首条红 (★S4 与 S8 逐字相同★)**:
```
❌ R4: 台账里同一条链的记录顺序打乱 ⇒ 仍取最新 ⇒ 必须绿
      实际红项 ['R6 硬保护: HW/PCB/demo_mainboard.kicad_pcb 锚点里有合法改板记录 (reboard) 但落表台账里查不到任何变更行 ⇒ 单号背书落不了地 = 红',
                'R6 硬保护: 受保护文件 md5 变了: HW/PCB/demo_mainboard.kicad_pcb (… ≠ 611b869e13518c3c023fb178f91a0075)']
❌ R5a: 台账最新记录的落表单号被改坏 ⇒ 必须红 ⇒ 用例本身坏了
反向用例: 5/7 通过
```

★**改前逐字 (★夹具的树构造 + 落表行工厂★)★**:
```python
# ★真件 L94~L102 · build_tree(): 从【真盘】整棵拷一份 ⇒ 拷出来的台账里【没有】那次合法改板的变更行 ★
def build_tree(tmp: str, root: str, name: str) -> str:
    """在 /tmp 里搭一棵完整的树 (★全拷贝 ⇒ 改它不会碰真盘★)。"""
    work = os.path.join(tmp, name)
    for rel in TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work
```

★**根因 (★本单实读·★归因到具体两行★)★**: ★**夹具把「盘面」拷进了临时树, 却没把「那次合法改板在落表台账里的变更行」一起拷进去** ⇒ ★硬保护件 md5 变了 · 台账里查不到对应变更行 ⇒ 两条硬保护红 ⇒ R4 期望绿 / R5a 期望红的【前置条件】被破坏 ★

**② `check_demo_panel_spec_r6_chainjudge_selftest.py` (★★改名特有·S4 红 / S8 绿★★)**

★**首条红 (★S4 实跑逐字★)**:
```
❌ CJ-1: 链头单号只改一处 (⇒ 台账自相矛盾) ⇒ 必须红
      ⇒ 用例本身坏了: 原单号 ISS-321 不在产出单号里了 (['ISS-9900']) ⇒ 改坏没生效
反向用例: 3/4 通过
```
★**对照 S8 (★零改名·同一道闸绿★)**:
```
★自证: 变体 ① 只改一处 (⇒ 台账自相矛盾): 改了 1 处 ⇒ 链头产出单号 = ['ISS-302', 'ISS-999'] ⇒ 判据: ★红★
```

★**改前逐字 (★真件 L284~L303 · CJ-1 用例 + 其破坏工具 L174~L214★)**:
```python
    # ---- CJ-1 (红): 只改一处 ⇒ 台账自相矛盾 ⇒ 必须红 (★修法 A★) ---------------------
    def case_cj1():
        work, anchors = fresh_tree(tmp, root, "cj1")
        p = ledger_path(work)
        base = rd(p)
        broken, hit = break_head_ticket_all(base, NET, bogus="ISS-9900", limit=1)
        ...
        st = gate.sw_ledger_state(NET, broken)
        prods = sorted((st.get("producer") or {}).get(head_net) or [])
        if st.get("head") != head_net:
            raise AssertionError("改单号把链头也改了 ⇒ 用例本身坏了")
        if true_iss not in prods:
            raise AssertionError("原单号 %s 不在产出单号里了 (%s) ⇒ 改坏没生效" % (true_iss, prods))
```

```python
# ★真件 L174~L214 · break_head_ticket_all(): ★只改【出现在链头产出记录里的】那些单号★ ★
def break_head_ticket_all(text: str, rel: str, bogus: str, limit: int = 0) -> tuple:
    """把【产出链头的那些记录】的落表单号, 在它【出现的每一处】都改掉 (★`limit` = 最多改几处★)。
    ...
    ★只改一处 = 台账自相矛盾 (⇒ 修法 A 治它) · 每一处都改 = 台账自洽但单号是假的 (⇒ 修法 B 治它)★
    """
```

★**根因 (★本单实读·★归因到具体那一步★)★**: ★**「只改一处 ⇒ 台账自相矛盾」这个前提, 要求链头【至少有两个产出记录】; 而改名之后网表 md5 变了 ⇒ 台账里只有【那一趟新落表的那一行】产出它 ⇒ 链头产出单号只有 1 个 ⇒ 改掉那 1 处就把真单号整个改没了 ⇒ 用例自证失败 ★**
★**⇒ 这不是夹具的错, 是【真实盘面变了】·夹具的假设没跟着变 ★**

**③ `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` (★S4 = S8 ⇒ 不是改名特有★)**

★**首条红 (★S4 实跑逐字★)**:
```
❌ HP-1/HP-2: 用例本身坏了: 链头取不准 (None)
❌ HP-4: 链头不唯一 = ['ba8aebf261b1', 'fadf2c2f6f49']
反向用例: 0/4 通过
```

★**改前逐字 (★真件 L118~L126 · build_tree(): 用 `gate.R6_TREE_FILES` 拷树★)**:
```python
def build_tree(tmp: str, root: str, name: str) -> str:
    """在临时目录里搭一棵完整的树 (★全拷贝 ⇒ 改它不会碰真盘★)。"""
    work = os.path.join(tmp, name)
    for rel in gate.R6_TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)                 # ★全拷贝 ⇒ 不用硬链接 (★有用例要改板★)
    return work
```

★**根因 (★本单实读★)★**: ★**硬保护件已经发生过一次真实合法改板 ⇒ 盘上同时存在【改板前 md5】与【改板后 md5】两个候选 ⇒ 链头取不准 / 不唯一 ⇒ HP-1~HP-4 的前置条件被破坏 ★**
★**⇒ S4 与 S8 同红 ⇒ 归因于【合法改板已发生过一次】⇒ 不是改名引起 ★**

#### §1-5-3 · ★**改后逐字 (★只给建议 + 代价 + 不改的后果 · ★need `iss321_decide_r6_selftest_fixture_after_reboard`·★本单不代拍★)**★

| 选项 | 改法 | 代价 | 不改的后果 |
|---|---|---|---|
| ★**甲** ★ | ★**把三个夹具的 `build_tree()` 从「拷真盘」改成「拷真盘 + 把那次合法改板的【落表变更行】一起补进临时树的台账」** ⇒ ★即【在已有链的基础上再追加一跳】而不是【从基线重新改】★ ★ | ★3 道夹具各改 `build_tree()` 一处 + 补一段台账行工厂 (★沿用 hardprot 那边已有的 `rows_for()` / `gate._row()` 口径★) ★ | 同下 |
| ★**乙** ★ | ★**把这一趟的期望值登记成【已知基线】** (★像 ISS-318 的 `BASELINE_TOKENS` / `BASELINE_COUNT` 那样) ⇒ ★**只对「硬保护件已改过一次」这一条登基线·其余照旧判红** ★ | ★**改受保护判据脚本 (★`check_demo_panel_spec_r6_*.py`★)·归 main 拍** ⇒ ★**方向是收紧还是放宽·必须一次说清★** ★ | 同下 |
| ★**丙** ★ | ★**不动夹具 · 只把三道闸从那一趟的门禁链里临时摘掉** ⇒ ★**明确写「摘掉哪几道 · 为什么 · 什么时候装回去」★ ★ | ★**门禁链少 3 道护栏** ⇒ ★**那一趟的板侧改动就没了这 3 道反向用例的覆盖** ⇒ ★**这是「拆护栏」不是「修护栏」** ★ | 同下 |

★**不改的后果 (★S4/S8 实测 + 推算★)★**: ★**三道闸在板那一趟当天就是红的** ⇒ ★**门禁链挂着 3 条恒红 ⇒ 掩盖真红** ⇒ ★**违反 ISS-309 铁律「不许把闸修成永远红」** ★
★**★本单建议 (★只给建议·不代拍★)★**: ★**选项甲** ⇒ ★**它是【让夹具跟上真实盘面】而不是【把判据改软】⇒ 判据方向一条没改·反向用例还在·覆盖不丢** ★
★**★但甲要动三道受保护夹具 ⇒ 归 main 拍 (★need `iss321_decide_r6_selftest_fixture_after_reboard`★)★**

---

### §1-6 · ★**第 6 件** ★ · `SW/BOARD_ONEPASS_SW_SYNC.md` 的 `SW01_PCB_MD5` 的 `current_state` 重锚 (★归属步 S9★)

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**6** ★ | `SW/BOARD_ONEPASS_SW_SYNC.md` | ★§1-6-2 的 `current_state` 原文 (★从盘上真件抄★) ★ | ★§1-6-3 的重锚读法 (★**板 md5 是 hex·不是位号·★闸零风险★) ★ | ★**L167** ★(★JSON 块里 `SW01_PCB_MD5` 的 `current_state` 那一行★) ★ | ★`python3 SW/tools/check_onepass_sw_sync.py` ⇒ ★**SW01 从红转绿** ★<br>★`python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=0** (★R6 硬保护段: 盘上板 md5 == 台账 `hard_protected[0].md5`★) ★ | ★**SW 域 (我)** · ★**归属步 S9** ★ | ★清单过期 ⇒ ★**W5 判红** ⇒ 「清单 current_state 里没有这个值 ⇒ 清单过期」 ★ | ★**必须同批** ★(★它就是 SW01 那一条·归属步 S9★) ★ |

#### §1-6-1 · 机制 (★闸怎么判的·逐字★)

```python
# ★SW/tools/check_onepass_sw_sync.py L171~L173 (★探针★):
    "SW01_PCB_MD5": (
        ["md5sum", os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")],
        r"([0-9a-f]{32})"),
# ★SW/tools/check_onepass_sw_sync.py L355~L360 (★判定★):
        val = m.group(1)
        state = str(it.get("current_state", ""))
        if val not in state:
            ok = False
            bad.append("%s: 盘面实测 = %r, 但清单 current_state 里没有这个值 ⇒ 清单过期" % (item_id, val))
```
★⇒ ★**判据就是一句话: 「盘上板的 md5 字符串必须出现在 `SW01_PCB_MD5` 那一条的 `current_state` 里」** ★

#### §1-6-2 · ★**改前逐字 (★真件 L167 · 一整行·★从盘上真件抄★)**★

```
      "current_state": "[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_protected[0].md5 钉的是同一个值 · R6 对该件走【纯 md5 比对独立分支】(SW/tools/check_demo_panel_spec.py L459~L472) ⇒ 盘上 ≠ 锚点即红, 无链头机制可依赖 ⇒ 那一趟改板当天必红 (ISS-275 只把「台账管的那两个文件」换成链头判决源, 硬保护两件不在链头机制里)",
```

#### §1-6-3 · ★**改后逐字 (★重锚的读法与落点 · ★归属步 S9★)**★

```bash
# ★★第 1 步: 读那一趟改完板之后的【新板 md5】 (★唯一权威读数★) ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb
# ★★第 2 步: 把上面输出的那个 32 位 hex 落到【两处】(★必须是同一处改·不许分两处各写一遍★)★★
#   ① SW/BOARD_ONEPASS_SW_SYNC.md L167 的 current_state 里的两处 md5:
#      「盘上板 md5 = <新值>」 + 「台账 §1 hard_protected[0].md5 钉的是同一个值」
#   ② 落表台账的 hard_protected[0].md5 (★由 S9 的合法重锚路径落★·★归 main→老板拍§4 三方案★)
# ★★第 3 步: 验 ★★
python3 SW/tools/check_onepass_sw_sync.py    # ★期望: SW01 不再红 (★整条闸仍可能因 SW08 红·见第 4 件★)★
python3 SW/tools/check_demo_panel_spec.py     # ★期望 rc=0 (R6 硬保护段: 盘上板 md5 == 台账 hard_protected[0].md5)★
```

★**★注意: 这一件的落点同时在【HW 侧的落表台账】上 ⇒ ★归属步 S9 ⇒ ★S9 的活·但【SW 侧那一半】是本清单这一条★ ★
★**★不许事后手改 `hard_protected` 的 md5** (★清单自己的 `action` 字段就写着这一句·★本清单不重复·★只强调★) ★

#### §1-6-4 · ★**为什么这一件【不是】改名引起的 (★归因清楚·别算到改名头上★)**★

★`SW01_PCB_MD5` 在 **S8 (零改名的对照组) 里也是红的** ⇒ ★**它是【板改了】引起的, 不是【改名】引起的** ★ ★[实测]
★⇒ ★**第 6 件与第 7 件的时序虽然都是「必须同批」, 但归因不同: 第 6 件是【板 md5 重锚】, 第 7 件是【文档位号同步】★**

---

### §1-7 · ★**第 7 件** ★ · `SW/*.md` 里的位号字面量 (★机器化改·★不逐条抄 671 处★)

| # | 改哪个文件 | 改前逐字 | 改后逐字 | 行号 / 定位锚点 | 验收命令 (★逐字可粘贴★) | 归属 | 不改的后果 | 时序 |
|---|---|---|---|---|---|---|---|---|
| ★**7** ★ | ★`SW/*.md` (★**41 份·其中 10 份有命中·共 671 处字面量**★) ★<br>★(`SW/tools/*.py` 的 153 行归第 1/2/3 件管·**本件不碰**★) ★ | ★§2-1 的真集 + 替换算法 (★机器口径·非手抄★) ★ | ★§2-2 的逐字命令 (★默认 dry-run★) ★ | ★**不适用** (★机器产物·不逐行抄★) ★ | ★`python3 SW/tools/check_sw_ref_reachability.py` ⇒ ★**rc=0** · `DESIGNATOR_DRIFT` = **0** · `DESIGNATOR_MISSING` = **3** (= 基线) ★ | ★**SW 域 (我)** ★ | ★闸判 **58 条改名漂移** (★S1 沙盒实测 `DESIGNATOR_DRIFT = 58`★) ⇒ ★**闸红** ⇒ **那一趟被自己的护栏卡住** ★ | ★**必须同批** ★ |

★**★这一件的特殊要求 (★任务书 §2① 点名的★)★**: ★**不许把 671 处逐条抄进清单** (★那份是机器产物★) ⇒ ★**本单交的是【怎么机器化改】+【改完怎么验】+【哪些是留证不能改】+【改完 58 条漂移会不会归零】** ★ ⇒ ★**见 §2** ★

---

## §2 · 第 7 件的机器化改法 (★专项展开★)

### §2-1 · 真集与替换算法 (★机器口径 · 非手抄★)

| 项 | 值 | 来源 |
|---|---|---|
| ★真集 (旧 → 新) ★ | ★**186 条** (★218 总集里「要改」的那 186 条·★「不动」的 32 条一条都不许碰★) ★ | `logs/iss321/rename_sets.json` 的 `map` 字段 (★`k != v` 的子集★) |
| ★扫描范围 ★ | ★**`SW/*.md` 41 份** (★**不含 `SW/tools/*.py`**★) ★ | `logs/iss323/14_rename_sw_docs_dryrun.txt` |
| ★有命中的文件 ★ | ★**10 份** (★其余 31 份 0 处·不用动★) ★ | 同上 |
| ★字面量替换处数 ★ | ★**671 处** ★ | 同上 |
| ★替换算法 ★ | ★**词边界精确字面量** (`(?<![A-Za-z0-9_])` + `(?![A-Za-z0-9_])`) ★**不是靠前缀猜** ★ | 同上 |
| ★替换顺序 ★ | ★**长的名字先替换** (★避免短名先替掉长名★) ★ | 同上 |

★**逐文件命中数 (★本单 11:5x 实测·★逐字搬自 dry-run 输出★)**★

| 文件 | 处数 | 位号个数 | 文件 | 处数 | 位号个数 |
|---|---:|---:|---|---:|---:|
| `SW/SW_TIMING_REVIEW.md` | **274** | 38 | `SW/POWER_STATE_SEMANTICS.md` | 3 | 3 |
| `SW/SHUTDOWN_SEMANTICS_SPEC.md` | **112** | 18 | `SW/RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md` | 1 | 1 |
| `SW/BOARD_ONEPASS_SW_SYNC.md` | **109** | 20 | `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` | 6 | 2 |
| `SW/ONETRIP_SW_RENAME_SAFETY.md` | **87** | 30 | `SW/SW_MD5_BASELINE_LEDGER.md` | 14 | 4 |
| `SW/LOAD_SWITCH_SELECTION_FACTS.md` | **34** | 4 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` | 31 | 5 |
| ★**合计** ★ | ★**671** ★ | — | ★**共 10 份有命中** ★ | — | — |

### §2-2 · ★**机器化改法 (★逐字可粘贴★)**★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★★第 1 步: 出计划 (★默认 dry-run·一个字节都不写★)★★
python3 logs/iss323/iss323_rename_sw_docs.py
# ★★第 2 步: 出副本 (★仍然一个字节都不碰项目真件★)★★
python3 logs/iss323/iss323_rename_sw_docs.py --apply --out /tmp/iss323_swdocs
# ★★第 3 步: 【归板那一趟】才把副本逐份覆盖回 SW/ ★★
# ★★第 4 步: 验 (★期望 rc=0 · DRIFT=0 ★)★★
python3 SW/tools/check_sw_ref_reachability.py
```

★**★为什么用脚本而不是一条 sed ★**:
★**位号名里含 `_` 和数字, 相邻位号可能互为前缀** ⇒ ★裸 `sed` 会替串 (★长名先被替掉 ⇒ 短名就再也替不到★) ⇒ ★**必须长名优先 + 词边界** ★
★**⇒ 脚本把这两个口径写死在代码里 ⇒ 复现口径唯一 ★**

### §2-3 · ★**哪些是留证不能改 (★本单实测读数·★这是第 7 件最要紧的一段★)**★

★**问题**: ★**体检报告类文档记录的【就是改名前的位号】** ⇒ ★把它们一起改名 ⇒ **历史体检记录被改写 ⇒ 证据链失真** ★
★**本单实测 (★场景 K · ★S2 的副本 + 把留证文档恢复成改名前原文★)★**:

| 读数 | 场景 S2 (全改) | ★场景 K (留证文档不改)★ | 判据 |
|---|---:|---:|---|
| `DESIGNATOR_DRIFT` | **0** | ★**28** ★ | 闸基线上限 = 0 ⇒ ★**红** ★ |
| `DESIGNATOR_MISSING` | **3** (★= 基线·绿★) | ★**5** ★ | 闸基线上限 = 3 ⇒ ★**红** ★ |
| ★新增真隐患是哪两条 ★ | — | ★**`R_CHG_LED_1` / `R_SER_USB_D_N_1`** ★ (★这俩是改名组·留证文档里留了旧名★) ★ | ★C14 兜底 ★ |

★**⇒ 结论 (★本单实测·不是推算★)★**: ★**留证文档【不改】⇒ 闸红 (28 条漂移 + 2 条新增真隐患) ; 【改】⇒ 闸绿但历史记录被改写** ★ ⇒ ★**这是一条【要拍板】的事 ⇒ need `iss321_decide_rename_doc_notation` ⇒ 本单不代拍** ★

★**三个选项 (★只给建议 + 代价★)★**:

| 选项 | 做法 | 闸 | 代价 |
|---|---|---|---|
| ★**甲** ★ | ★**全改 (41 份全改)** ⇒ 留证文档的旧名也一起改 ★ | ★**绿** (DRIFT 0 / MISSING 3) ★ | ★**历史体检记录被改写** ⇒ ★**ISS-321 的结论与本清单的「改前逐字」列在改名后【不再成立】** ★ |
| ★**乙** ★ | ★**留证文档排除** (`--exclude`) ⇒ 但它们【还在 `SW/` 里】⇒ 闸仍扫到 ★ | ★**红** (DRIFT 28 / MISSING 5) ★ | ★**闸红 ⇒ 那一趟被自己的护栏卡住** ⇒ ★**必须配套「把它们移出 `SW/`」或「给闸加显式豁免」★ ★** |
| ★**丙** ★ | ★**把留证文档迁出 `SW/` (★落 `logs/`·★闸不扫★) ⇒ 同时在 `SW/` 留一个指针 ★ | ★**绿** ★ | ★**改既有文档的落点 (★一次性的迁移动作★) ⇒ ★**闸的扫描范围是 `SW/*.md` (★`DOC_GLOB`★) ⇒ 迁出去就不扫了** ★ |

★**★本单建议 (★只给建议·不代拍★)★**: ★**选项丙** ⇒ ★**它同时满足「闸绿」与「证据保真」·代价是一次性的落点迁移 ⇒ ★比甲多花一次迁移·比乙少一次改闸** ★
★**★但这是「文档落点 / 闸的扫描范围」口径的改动 ⇒ 归 main 拍 (★need `iss321_decide_rename_doc_notation`★)★**

### §2-4 · ★**「58 条漂移会不会归零」 (★本单实测·逐字回答★)**★

| 问题 | 答案 | 依据 |
|---|---|---|
| ★**改名后文档不同步 ⇒ 漂移多少条** ★ | ★**58 条** (★`DESIGNATOR_DRIFT = 58`★) ★ | ★S1 沙盒实跑 `logs/iss323/raw_rootS1_check_sw_ref_reachability.txt` L13 ★ |
| ★**改名后文档同步 ⇒ 漂移多少条** ★ | ★**0 条** (★`DESIGNATOR_DRIFT = 0`·`DESIGNATOR_MISSING = 3` = 基线 ⇒ rc=0★) ★ | ★S2 沙盒实跑 `logs/iss323/raw_rootS2_check_sw_ref_reachability.txt` L13~L14 ★ |
| ★**⇒ 会归零吗** ★ | ★**会 —— 但前提是【第 1 件的冻结表重建】+【第 7 件的文档同步】两件都做完★** ★ | ★S2 场景 = 板/表改名 + 文档同步改 ⇒ DRIFT 0 ★ |
| ★**★注意 (★顺序★)** ★ | ★**第 1 件 (冻结表重建) 必须在第 7 件 (文档同步)【之后】跑** ★ ⇒ ★**因为 `--freeze-registry` 是按【当前盘面】重新分类的 ⇒ 文档还没同步时重建 ⇒ 冻结表会把【还没改的旧名】当成 live 收进去 ⇒ 顺序反了 ⇒ 闸照样红 ★ ★[推算]·依据 = `--freeze-registry` 的实现 (`freeze_registry()` L793~L823 · ★它对每个文档 token 调 `classify()`·只留 `DESIGNATOR_OK`★)★** ★ |

---

## §3 · 第 5 件的夹具改法建议 (★专项展开 · ★只给建议 + 代价 + 不拍的后果★)

★**§1-5 已经把三道闸的逐条根因抄全了; 本节只回答一件事: ★**改法该怎么写才「不改判据方向」** ★**

★**三条共同的不变量 (★改法必须守住★)**★:
1. ★**反向用例还得是反向用例** (★改坏盘面 ⇒ 判据必须红; 没改坏 ⇒ 判据必须绿★) ★
2. ★**不许把闸修成永远红** (★ISS-309 铁律★) ⇒ ★**不许用「登记成基线」偷懒** ⇒ ★**选项乙的「只对这一条登基线」是可接受的·但【整道闸登基线】不可接受** ★
3. ★**改的是夹具, 不是判据** ⇒ ★**`check_demo_panel_spec.py` 的判决逻辑一个字都不许动** ★

★**逐条建议 (★每条都写清「改哪一行 · 为什么这样改 · 代价」★)**★:

| 闸 | 建议改法 (★方向不变★) | 改哪一处 | 代价 |
|---|---|---|---|
| `..._r6_selftest.py` | ★**`build_tree()` 之后补一步: 把【那次合法改板在落表台账里的变更行】按 `gate._row()` 口径补进临时树的台账** ⇒ ★R4 的「盘上 md5 变了」与「台账里有变更行」两条硬保护同时成立 ★ | ★真件 `build_tree()` (L94~L102) 之后 + R4/R5a 两个用例的树构造 ★ | ★一处函数 + 两个用例的树构造 ★ |
| `..._r6_chainjudge_selftest.py` | ★**CJ-1 的前提是「链头至少有两个产出记录」⇒ 改法: 在 `case_cj1()` 里【先构造出两个产出记录】(★把链头那一行复制一份 + 给副本换个单号★) ⇒ 再「只改其中一处」⇒ 才是真正的「台账自相矛盾」 ★ | ★真件 `case_cj1()` (L284~L303) + `break_head_ticket_all()` 的调用参数 (★`limit=1` 的语义保持不变★) ★ | ★一处用例 + 一个构造步骤 ★ |
| `..._hardprot_iss315_selftest.py` | ★**HP-1~HP-4 的前提是「链头唯一」⇒ 改法: 用例的临时树里【只留改板后的那一个 md5】(★或显式指定链头★) ⇒ 链头取得准 ★ | ★真件 `build_tree()` (L118~L126) 之后 + 各用例的树构造 ★ | ★一处函数 + 若干用例的树构造 ★ |

★**★本单不代拍 (★need `iss321_decide_r6_selftest_fixture_after_reboard`★)★**:
> ★**问法 (一句话)**: ★**「三道 R6 selftest 闸的夹具假设『硬保护件从没被合法改过 / 链头只有一个产出记录』⇒ 板那一趟做完一次合法改板后它们恒红 (S4 与 S8 实测同红) —— 夹具改成『在已有链上再追加一跳』(选项甲), 还是把这一趟的期望值登记成已知基线 (选项乙) —— 批哪一条?」**
> ★**不批的后果**: ★**三道闸在那一趟当天就红 ⇒ 门禁链挂着 3 条恒红 ⇒ 掩盖真红 ⇒ 违反 ISS-309 铁律「不许把闸修成永远红」** ★ ★[实测 S4/S8 + 推算]★

---

## §4 · 第 6 件的板 md5 重锚 (★读法与落点 · 归属步 S9★)

★**§1-6 已经给了逐字读法与落点; 本节只补三件容易做错的事**★

| # | 容易做错的 | 正解 |
|---|---|---|
| ① | ★**只改 `SW/BOARD_ONEPASS_SW_SYNC.md` 一处** ⇒ 台账 `hard_protected[0].md5` 还是旧值 ⇒ ★`check_demo_panel_spec.py` 的 R6 硬保护段照样红 ★ | ★**两处必须同批**: 落表台账的 `hard_protected[0].md5` + `SW/BOARD_ONEPASS_SW_SYNC.md` L167 的 `current_state` ★ |
| ② | ★**顺手把 `.kicad_pro` 也重锚** ⇒ 那是 SW02 那一条, 归 S9 的另一件事 ⇒ ★**别把两条混着改** ★ | ★`.kicad_pro` 的 md5 与板的 md5 要【同批】重锚 (★清单 L179 写着这一句★) ★ |
| ③ | ★**事后手改 `hard_protected` 的 md5** ⇒ ★**这是 ISS-275 明确禁止的** (★锚点必须走合法重锚路径·不许手改★) ★ | ★走 S9 的合法重锚路径 (★方案 ①②③ 三选一·★归 main→老板拍·★本清单不代拍★) ★ |

★**★归属步的一句话★**: ★**第 6 件是 S9 的活·但【SW 侧那一半】就是本清单这一条 ⇒ ★它和另外 6 件一样【必须与板那一趟同批】★ ★

---

## §5 · 执行顺序 · 「板只改一次」的时序

### §5-1 · ★**7 件的同批顺序 (★背靠背·不许拆成两趟★)**★

| 序 | 件 | 为什么必须在这个位置 |
|---|---|---|
| ★**0** ★ | ★**板侧那一趟 (★不属本单★)** ★ | ★位号改名 + 板侧同步 B-1~B8 + 布局修正 + 布线 45→0 + Gerber/投产包重出 · 同一趟 ★ |
| ★**1** ★ | ★**第 7 件** (文档同步改名) ★ | ★**先改文档** ⇒ 第 1 件的冻结表重建才收得对 (★§2-4 的顺序结论★) ★ |
| ★**2** ★ | ★**第 1 件** (冻结表按改名后盘面重建) ★ | ★必须在第 7 件之后 (★`--freeze-registry` 按当前盘面分类★) ★ |
| ★**3** ★ | ★**第 2 件** (`timing_check.py` 位号解析层) ★ | ★独立于前两件·但要一起做 (★它闸的是板/表, 不闸文档★) ★ |
| ★**4** ★ | ★**第 3 件** (三条现状探针) ★ | ★独立 ★ |
| ★**5** ★ | ★**第 4 件** (★跨域·hw-lead★) ★ | ★必须同批 · ★SW 侧【无权碰】⇒ ★交 need ★ |
| ★**6** ★ | ★**第 5 件** (三道 R6 夹具) ★ | ★独立 · 但要在门禁链跑之前装好 ★ |
| ★**7** ★ | ★**第 6 件** (板 md5 重锚) ★ | ★S9 · ★要在板出之后、门禁链跑之前 ★ |

### §5-2 · ★**门禁链的验收 (★那一趟的「交作业」标准★)**★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py
# ★期望 rc=0 · Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿★
```
★**⇒ 7 件做完 ⇒ 这条命令必须 rc=0 ⇒ ★**这才是「板只改一次那一趟」的成功判据** ★**

### §5-3 · ★**未决项 (★need · ★本单不代拍★)**★

| # | need key | 一句话问法 | 不拍的后果 |
|---|---|---|---|
| ★**1** ★ | ★`iss321_decide_rename_batch_scope` ★ | ★**「板只改一次那一趟的 SW 侧同批改动清单是【7 件】(改法已逐条沙盒验证·rc 都实测过) —— 批不批这 7 件? 另外 HW 侧 `HW/check_netlist_selfconsistency.py` 的 16 个位号 (116 处·hw-lead 的域) 要不要连 hw-lead 的一起改?」** ★ | ★**不批 ⇒ 那一趟的门禁链 day-1 就红 (至少 4 道闸) ⇒ 那一趟被自己的护栏卡住 ⇒ 「板只改一次」变成「板改两次」** ★ ★[推算]★ |
| ★**2** ★ | ★`iss321_decide_r6_selftest_fixture_after_reboard` ★ | ★**「三道 R6 selftest 闸的夹具假设『硬保护件从没被合法改过 / 链头只有一个产出记录』⇒ 板那一趟做完一次合法改板后它们恒红 —— 夹具改成『在已有链上再追加一跳』(选项甲), 还是登记成已知基线 (选项乙) —— 批哪一条?」** ★ | ★**三道闸在那一趟当天就红 ⇒ 门禁链挂着 3 条恒红 ⇒ 掩盖真红 ⇒ 违反 ISS-309 铁律** ★ ★[实测 S4/S8]★ |
| ★**3** ★ | ★`iss321_sw_docs_rename_bulk_24files` ★ | ★**「SW 侧 41 份 md 里的 671 处位号字面量要随改名同步改 (类别 ②·不改不红·但改了才准) —— 这批文档改动跟板那一趟同批做, 还是板出之后单开一单做?」** ★ | ★**跟板那一趟同批 ⇒ 板出之后闸判 58 条改名漂移 (S1 实测) ⇒ 闸红; 单开一单 ⇒ 板出之后有一段时间闸是红的 (但不是假红·是真漂移·符合 ISS-318 的设计意图)」** ★ |
| ★**4** ★ | ★`iss321_decide_rename_doc_notation` ★ | ★**「SW 侧任何要写『改名后名』或『形状像位号但不是位号』的文档 (★改名方案文档 / 作业包 / 交接页★) —— 是统一规定『写进 `logs/` 不进 `SW/`』 (选项丙), 还是给 ISS-318 的闸加一条『改名方案文档』的显式豁免?」** ★ | ★**本单实测: 场景 K (留证文档不改) ⇒ 闸判 28 条漂移 + 2 条新增真隐患 ⇒ 闸红 ⇒ ★**任何写这类文档的人都会踩同一个坑** ⇒ 要么规定写法 (★本单已按「不写死改名后名」改过一遍·实测绿★), 要么闸加豁免 (★改闸 = 受保护资产·由 main 拍★)** ★ ★[实测]★ |

---

## §6 · 证据分级 · 复现命令 · 边界自证

### §6-1 · 证据分级

| 结论 | 分级 | 依据 |
|---|---|---|
| ★改名宇宙 218 / 要改 186 / 不动 32 ★ | ★**[实测]** ★ | ★本机实跑 `logs/iss321/iss321_parse_rename_sets.py` + 三条自检全过 ★ |
| ★80 次沙盒 rc 矩阵 (8 场景 × 10 闸) ★ | ★**[实测]** ★ | ★本单 11:5x 重跑 · `logs/iss323/09_rc_matrix.txt` + 80 份 `raw_rootS*.txt` ★ |
| ★改名特有 3 道闸 (timing_check / adc_sync / chainjudge) ★ | ★**[实测]** ★ | ★S4 红 + S8 绿 ★ |
| ★`timing_check.py` 崩在 L1113 (`TypeError`) ★ | ★**[实测]** ★ | ★S4 沙盒 traceback 逐字 ★ |
| ★F-1 改 17 处原子替换 ⇒ rc=0 · SELFTEST 85/85 ★ | ★**[实测]** ★ | ★本单沙盒副本实跑 · `logs/iss323/13_verify_fix20.txt` ★ |
| ★F-1 改 25 处 (ISS-321 原版) ⇒ rc=0 · SELFTEST 85/85 ★ | ★**[实测]** ★ | ★本单重跑 ISS-321 的脚本 · `logs/iss323/10_verify_fix.txt` ★ |
| ★F-1 的 5 处断言加固【不必做】 ★ | ★**[实测]** ★ | ★17 处版与 25 处版读数完全相同 ★ |
| ★上游 `adc_sync` 改后 rc=0 · 29/29 ★ | ★**[实测]** ★ | ★沙盒 `fixroot20` 实跑 ★ |
| ★F-2 改 3 处 ⇒ SW03/SW04/SW05 三条转绿 ★ | ★**[实测]** ★ | ★沙盒副本实跑 · `logs/iss323/11_verify_f2.txt` ★ |
| ★F-3 重建冻结表 = 78 条 (60 改名组 + 18 不动组) · rc=0 · DRIFT 0 ★ | ★**[实测]** ★ | ★沙盒副本实跑 · `logs/iss323/12_f3_registry_after_rename.txt` ★ |
| ★跨域 16 个位号 / 116 处 (全文件 19 / 136) ★ | ★**[实测]** ★ | ★本单独立复算 + 与 ISS-321 §2 交叉验证一致 ★ |
| ★第 7 件 41 份 md / 10 份有命中 / 671 处 ★ | ★**[实测]** ★ | ★dry-run 实跑 · `logs/iss323/14_rename_sw_docs_dryrun.txt` ★ |
| ★留证文档不改 ⇒ 闸判 28 条漂移 + 2 条新增真隐患 ★ | ★**[实测]** ★ | ★场景 K 沙盒实跑 · `logs/iss323/15_sb_keep_evidence.txt` ★ |
| ★改名后文档不同步 ⇒ 58 条漂移 ; 同步后 ⇒ 0 条 ★ | ★**[实测]** ★ | ★S1 / S2 沙盒实跑 ★ |
| ★第 1 件必须在第 7 件之后 ★ | ★**[推算]** ★ | ★依据 = `--freeze-registry` 的实现 (`freeze_registry()` 按当前盘面调 `classify()`) ★ |
| ★「改晚了 ⇒ 闸红在投产包上 ⇒ 要重出一次」 ★ | ★**[推算]** ★ | ★依据 = ISS-314/317 已算清的「板只改一次」语义 + 本清单 §5-1 的时序推理 ★ |
| ★门禁链当天会红 ⇒ 那一趟被护栏卡住 ★ | ★**[推算]** ★ | ★依据 = `state/gate_check.py` 的挂链清单 + 本单的 80 次实跑读数 ★ |

★**★本单无 [官网] / [媒体] / [0数据] 条目: 全部结论来自本机实读与沙盒实跑 ★**

### §6-2 · ★**一条命令复现全部 (★逐字可粘贴★)**★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ---- ① 机器解析 (★7 件清单的数据源·不许手抄★) ----
python3 logs/iss321/iss321_parse_rename_sets.py
python3 logs/iss321/iss321_scan_sw_refs.py
python3 logs/iss321/iss321_make_tsv.py
# ---- ② 跨域逐行扫描 (★第 4 件的逐字清单★) ----
python3 logs/iss323/iss323_hw_crossdomain_scan.py
# ---- ③ 改法锚点 → 真件行号 (★第 1/2/3 件的定位串★) ----
python3 logs/iss323/iss323_anchor_locate.py
# ---- ④ 沙盒造场 + 实跑 (★8 场景 × 10 闸 = 80 次★) ----
python3 logs/iss321/iss321_sb_make.py
python3 logs/iss321/iss321_sb_make_s3.py
python3 logs/iss321/iss321_sb_make_s4.py
python3 logs/iss321/iss321_sb_make_s5.py
python3 logs/iss321/iss321_sb_make_s7.py
python3 logs/iss321/iss321_sb_make_s8.py
bash    logs/iss321/iss321_sb_run.sh
bash    logs/iss323/iss323_sb_run_all.sh
# ---- ⑤ 改法验证 (★真闸零改★) ----
python3 logs/iss321/iss321_verify_fix.py        # ★F-1 (25 处原版) + F-2 (v1) + F-3★
python3 logs/iss321/iss321_verify_f2.py         # ★F-2 改名无关版 (★最终采用★)★
python3 logs/iss323/iss323_verify_fix20.py      # ★F-1 精简版 (★17 处·★本单新发现★)★
python3 logs/iss323/iss323_sb_keep_evidence.py  # ★第 7 件的留证选项实测★
# ---- ⑥ 第 7 件的机器化改法 (★默认 dry-run★) ----
python3 logs/iss323/iss323_rename_sw_docs.py
# ---- ⑦ 门禁链 + 零写板双证 ----
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb
# ---- ⑧ 本单两份交卷文档 × ISS-318 闸预演 (★踩坑自检★) ----
python3 logs/iss323/iss323_doc_gate_check.py
```

### §6-3 · ★**边界自证 (★逐条 · ★全部 md5 实测·★落 `logs/iss323/99_zerowrite_proof.txt`★)**★

| 纪律 | 自证 |
|---|---|
| ★**零写板** ★ | ★`HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` ★[实测] |
| ★**零落表** ★ | ★网表 / 脚表 / BOM / 原理图 真件 md5 全部不变 (★沙盒只出副本到 `tmp/iss321_sandbox/`★) ★ |
| ★**零改闸** ★ | ★`SW/tools/*.py` 全部文件 md5 不变 ★[实测] (★改法只落在 `tmp/iss321_sandbox/fixroot*/` 的副本上★) ★ |
| ★**零改既有文档正文** ★ | ★`SW/*.md` 真件 md5 全部不变 ★[实测] (★第 7 件的 671 处只给命令·默认 dry-run★) ★ |
| ★**沙盒只写 `tmp/` + `logs/iss323/`** ★ | ★`tmp/iss321_sandbox/{rootS0..rootS8, fixroot, fixroot2, fixroot20}` + `logs/iss323/` ★ |
| ★**零外发** ★ | ★本单**没有发任何邮件 / 询价 / 问询 / 采购** ⇒ 全部靠本机实读 + 沙盒实跑 ★[实测] |
| ★**不替老板拍板** ★ | ★§5-3 四条 need 交 main 拍 ⇒ 本单不代拍 ★ |
| ★**不自签 issue_log** ★ | ★`state/issue_log.yaml` 一个字节没动 ★[实测] |
| ★**不碰别人的域** ★ | ★`HW/check_netlist_selfconsistency.py` 只读 · 只给改法 · 没改 ★[实测] |
| ★**不写别人的分片** ★ | ★只写 `state/fragments/sw.yaml` (★经 `state/frag_write.py --agent sw-lead` 原子写★) ★ |

### §6-4 · ★**本单产出的文件清单 ★**

| # | 文件 | 内容 |
|---|---|---|
| 1 | ★`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` ★ | ★本单主交卷页 (★本文件·7 件 × 9 字段·§0~§6★) ★ |
| 2 | ★`HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` ★ | ★给 main 的交卷单 (B0~B6) ★ |
| 3 | ★`logs/iss323/` (★机器原始输出·4 类齐全★) ★ | ★解析 (01~04) + 沙盒 (05~15) + 门禁 (98) + 零写板双证 (99) ★ |
| 4 | ★`state/fragments/sw.yaml` ★ | ★sw 分片 (★经 `state/frag_write.py --agent sw-lead` 原子写★) ★ |
