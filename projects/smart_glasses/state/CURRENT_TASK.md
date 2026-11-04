# CURRENT_TASK —— 当前在做什么 (board_progress.py 会读前 4 行)

1. 最高优先级: 自研 demo 主板 → 可下单 (ISS-181 / ISS-182)
2. 修①: J_USB_C 自绘 GCT USB4105-16p 真封装 + 挪到板边 (现为通用 8 脚假封装, 摆板中央 ⇒ 插不了线)
3. 修②: 路由器补 MIPI 差分配平 (CSI 时钟对 Δ32.4mm / DSI Δ16.5mm 未配平)
4. 修③: GND 缝合 (36 个 GND 焊盘缺过孔) + NC_CONN_CAM 8 个查是否假未连接
5. 修④: 剩余 ~57 未连接 (SoM BTB 密集区 ~25 个信号网)
6. 收尾: unconnected=0 + DRC=0 + Gerber 重出 ⇒ 投板放行清单 (G1 过)
7. 纪律: 同一块板不能我和子 agent 同时写; 回执数字必须能在留证文件里对上
