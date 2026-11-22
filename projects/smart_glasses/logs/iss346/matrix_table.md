### 机器生成矩阵 (由 `SW/tools/gen_storage_capacity_matrix.py` 实跑渲染)

证据: [实测] PC 侧静态布局检查 (被测对象 = SW/tools/s2_rescue_config.example.json 的partition_layout 副本 + flash_layout_check.py 的判定逻辑); partition_layout 本身是 [推算] 占位值 ⇒ 结论等级 = [推算]

| rootfs | 64MB NOR | 128MB NOR | 256MB NOR | 8GB eMMC |
|---|---|---|---|---|
| **20 MB** | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=79724544 > 设备容量 67108864`<br>占用 76.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | 装得下<br>`PASS ⇒ PASS 占用 79724544 / 134217728 字节 (59.4%), 未越界`<br>占用 76.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 79724544 / 268435456 字节 (29.7%), 未越界`<br>占用 76.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 79724544 / 8589934592 字节 (0.9%), 未越界`<br>占用 76.031 MiB · 槽缩: 否 |
| **30 MB** | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=90210304 > 设备容量 67108864`<br>占用 86.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | 装得下<br>`PASS ⇒ PASS 占用 90210304 / 134217728 字节 (67.2%), 未越界`<br>占用 86.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 90210304 / 268435456 字节 (33.6%), 未越界`<br>占用 86.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 90210304 / 8589934592 字节 (1.1%), 未越界`<br>占用 86.031 MiB · 槽缩: 否 |
| **40 MB** | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=100696064 > 设备容量 67108864`<br>占用 96.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | 装得下<br>`PASS ⇒ PASS 占用 100696064 / 134217728 字节 (75.0%), 未越界`<br>占用 96.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 100696064 / 268435456 字节 (37.5%), 未越界`<br>占用 96.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 100696064 / 8589934592 字节 (1.2%), 未越界`<br>占用 96.031 MiB · 槽缩: 否 |
| **64 MB** | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=125861888 > 设备容量 67108864`<br>占用 120.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | 装得下<br>`PASS ⇒ PASS 占用 125861888 / 134217728 字节 (93.8%), 未越界`<br>占用 120.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 125861888 / 268435456 字节 (46.9%), 未越界`<br>占用 120.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 125861888 / 8589934592 字节 (1.5%), 未越界`<br>占用 120.031 MiB · 槽缩: 否 |
| **128 MB** | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=192970752 > 设备容量 67108864`<br>占用 184.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | **装不下**<br>`FAIL ⇒ 最后一个分区 version_block end=192970752 > 设备容量 134217728`<br>占用 184.031 MiB · 槽缩: 是 (model 15→11 MiB 后**仍装不下**) | 装得下<br>`PASS ⇒ PASS 占用 192970752 / 268435456 字节 (71.9%), 未越界`<br>占用 184.031 MiB · 槽缩: 否 | 装得下<br>`PASS ⇒ PASS 占用 192970752 / 8589934592 字节 (2.2%), 未越界`<br>占用 184.031 MiB · 槽缩: 否 |

#### 每列的 rootfs 装得下上限 (解析解 + 实跑自证)

| 存储 | model 槽 | rootfs 上限 | 实跑自证 |
|---|---|---|---|
| 64MB NOR | 15.0 MiB | **7.969 MiB** (8355840 B) | rootfs=8355840B (7.969 MiB) → LAY-03 PASS / rootfs=9404416B (8.969 MiB) → LAY-03 FAIL |
| 64MB NOR | 11.0 MiB | **15.969 MiB** (16744448 B) | rootfs=16744448B (15.969 MiB) → LAY-03 PASS / rootfs=17793024B (16.969 MiB) → LAY-03 FAIL |
| 128MB NOR | 15.0 MiB | **71.969 MiB** (75464704 B) | rootfs=75464704B (71.969 MiB) → LAY-03 PASS / rootfs=76513280B (72.969 MiB) → LAY-03 FAIL |
| 128MB NOR | 11.0 MiB | **79.969 MiB** (83853312 B) | rootfs=83853312B (79.969 MiB) → LAY-03 PASS / rootfs=84901888B (80.969 MiB) → LAY-03 FAIL |
| 256MB NOR | 15.0 MiB | **199.969 MiB** (209682432 B) | rootfs=209682432B (199.969 MiB) → LAY-03 PASS / rootfs=210731008B (200.969 MiB) → LAY-03 FAIL |
| 256MB NOR | 11.0 MiB | **207.969 MiB** (218071040 B) | rootfs=218071040B (207.969 MiB) → LAY-03 PASS / rootfs=219119616B (208.969 MiB) → LAY-03 FAIL |
| 8GB eMMC | 15.0 MiB | **8135.969 MiB** (8531181568 B) | rootfs=8531181568B (8135.969 MiB) → LAY-03 PASS / rootfs=8532230144B (8136.969 MiB) → LAY-03 FAIL |
| 8GB eMMC | 11.0 MiB | **8143.969 MiB** (8539570176 B) | rootfs=8539570176B (8143.969 MiB) → LAY-03 PASS / rootfs=8540618752B (8144.969 MiB) → LAY-03 FAIL |

#### 缩槽能挤出的余量 (model 槽 15→11 MiB · app 槽不动)

| 存储 | rootfs 上限 (model 15 MiB) | rootfs 上限 (model 11 MiB) | 可挤出 |
|---|---|---|---|
| 64MB NOR | 7.969 MiB | 15.969 MiB | **+8.0 MiB** (= 2×(15−11) MiB) |
| 128MB NOR | 71.969 MiB | 79.969 MiB | **+8.0 MiB** (= 2×(15−11) MiB) |
| 256MB NOR | 199.969 MiB | 207.969 MiB | **+8.0 MiB** (= 2×(15−11) MiB) |
| 8GB eMMC | 8135.969 MiB | 8143.969 MiB | **+8.0 MiB** (= 2×(15−11) MiB) |

★app 槽 (2×8 MiB) 是**第二根杠杆**, 但 app 产物体积是 [0数据] ⇒ 它的可缩量**上界未定** ⇒ 本矩阵不猜.

#### 每格 LAY-08 (rootfs 分档) 原始判定

| rootfs | 64MB NOR | 128MB NOR | 256MB NOR | 8GB eMMC |
|---|---|---|---|---|
| **20 MB** | PASS ⇒ PASS rootfs = 20.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 20.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 20.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 20.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 |
| **30 MB** | PASS ⇒ PASS rootfs = 30.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 30.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 30.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 | PASS ⇒ PASS rootfs = 30.0MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立 |
| **40 MB** | PASS ⇒ PASS rootfs = 40.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 40.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 40.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 40.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR |
| **64 MB** | PASS ⇒ PASS rootfs = 64.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 64.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 64.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR | PASS ⇒ PASS rootfs = 64.0MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR |
| **128 MB** | FAIL ⇒ rootfs = 128.0MB (>64MB) → SPI-NOR 方案出局, 必须 eMMC (板宽 12→15mm) | FAIL ⇒ rootfs = 128.0MB (>64MB) → SPI-NOR 方案出局, 必须 eMMC (板宽 12→15mm) | FAIL ⇒ rootfs = 128.0MB (>64MB) → SPI-NOR 方案出局, 必须 eMMC (板宽 12→15mm) | FAIL ⇒ rootfs = 128.0MB (>64MB) → SPI-NOR 方案出局, 必须 eMMC (板宽 12→15mm) |
