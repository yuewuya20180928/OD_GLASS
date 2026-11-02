#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 RK3572 的「球位号」和「pinctrl 复用」两层合并 → 项目可直接用的引脚分配表
================================================================================
★两层数据源 (证据等级):
  ① 球位号层: Rockchip 官方 Datasheet V1.1 §2.6 Pin Number List  [官方]
     → `rk3572_pins.json` (550 球, 本目录 parse_rk3572_datasheet.py 生成)
  ② 复用层:   Rockchip 官方 BSP kernel develop-6.12 的 rk3572-pinctrl.dtsi  [官方-BSP]
     → `rk3572-pinctrl.dtsi` (822 信号名 / 1121 mux 条目)
     格式: <gpio_bank RK_Pxx mux_func &pcfg_*>   例: <0 RK_PA0 3 &pcfg_pull_none>

★为什么要合并:
  Datasheet 给的是「这个球是什么功能」(固定功能脚, 如 MIPI_DPHY_DSI_TX_CLKP = 球 AT27)
  pinctrl 给的是「GPIO 复用成什么功能」(GPIO0_A0 能复用成 i2c0_scl / uart0_tx ...)
  ★**56 个占位符里两类都有**, 不合并就会出现"DSI 有球号但 GPIO 信号没球号"的错觉。

★输出: rk3572_pin_assign.csv / .json  (信号 → 球位号 → mux → 证据)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PINS = os.path.join(HERE, "rk3572_pins.json")
PINCTRL = os.path.join(HERE, "rk3572-pinctrl.dtsi")
OUT_CSV = os.path.join(HERE, "rk3572_pin_assign.csv")
OUT_JSON = os.path.join(HERE, "rk3572_pin_assign.json")

# 项目网表里 56 个 SoC 占位符信号 (从 HW/netlist_v1.csv 提取, 硬编码做自检对照)
PROJECT_SIGNALS = [
    "DSI_TX_CK_P", "DSI_TX_CK_N", "DSI_TX_D0_P", "DSI_TX_D0_N",
    "DSI_TX_D1_P", "DSI_TX_D1_N", "DSI_TX_D2_P", "DSI_TX_D2_N",
    "DSI_TX_D3_P", "DSI_TX_D3_N",
    "CSI_D0_CK_P", "CSI_D0_CK_N", "CSI_D0_D0_P", "CSI_D0_D0_N",
    "CSI_D0_D1_P", "CSI_D0_D1_N", "CSI_D0_D2_P", "CSI_D0_D2_N",
    "CSI_D0_D3_P", "CSI_D0_D3_N",
    "CSI_MCLK", "CSI_RESET_N",
    "I2C_A_SCL", "I2C_A_SDA", "I2C_B_SCL", "I2C_B_SDA",
    "SPI_SCLK", "SPI_MOSI", "SPI_MISO", "SPI_CSn",
    "UART_TX", "UART_RX",
    "USB_D_P", "USB_D_N", "USB_VBUS_DET",
    "JTAG_TMS", "JTAG_TDO", "JTAG_TDI", "JTAG_TCK",
    "FSIN", "PWR_CTRL", "BOOT_N", "RESET_N",
    "XTAL_IN", "XTAL_OUT", "BAT_DET",
    "KEY_VOL_P", "KEY_VOL_M", "KEY_PWR", "KEY_CAM",
    "LED_R", "LED_G", "LED_B", "ID0", "ID1",
]


def parse_pinctrl(path: str) -> dict[str, list[dict]]:
    """signal_name -> [{bank, pin, mux}]"""
    if not os.path.exists(path):
        raise SystemExit(f"❌ 缺 {path}")
    src = open(path, encoding="utf-8", errors="ignore").read()
    pat = re.compile(r"/\*\s*([a-z0-9_]+)\s*\*/\s*\n\s*<(\d+)\s+(RK_P[A-Z0-9_]+)\s+(\d+)")
    out: dict[str, list[dict]] = {}
    for name, bank, pin, mux in pat.findall(src):
        out.setdefault(name, []).append({"bank": int(bank), "pin": pin, "mux": int(mux)})
    return out


def gpio_name(bank: int, pin: str) -> str:
    """RK_PA0 -> GPIO0_A0"""
    m = re.match(r"RK_P([A-Z])([0-9]+)$", pin)
    if not m:
        return pin
    letter, idx = m.group(1), int(m.group(2))
    return f"GPIO{bank}_{letter}{idx}"


def main() -> int:
    if not os.path.exists(PINS):
        raise SystemExit(f"❌ 缺 {PINS}")
    pins = json.load(open(PINS, encoding="utf-8"))
    pinctrl = parse_pinctrl(PINCTRL)

    # 球位号 → (功能名, gpio缩写)
    ball_by_func: dict[str, dict] = {}
    for p in pins:
        for fn in p["name"].split("/"):
            fn = fn.strip()
            if fn and fn not in ball_by_func:
                ball_by_func[fn] = p

    # 项目信号 → 候选引脚
    # ① 固定功能脚 (datasheet 直接给球): DSI_TX_* / CSI_*_RX_* / USB_DRD0_*
    # ② pinctrl 复用脚 (bank/pin → 找 datasheet 里 gpio 缩写匹配的那一球)
    gpio_to_ball: dict[str, dict] = {}
    for p in pins:
        g = (p.get("gpio") or "").strip()
        if g:
            gpio_to_ball.setdefault(g.upper(), p)

    FIXED = {
        "DSI_TX_CK_P": "MIPI_DPHY_DSI_TX_CLKP", "DSI_TX_CK_N": "MIPI_DPHY_DSI_TX_CLKN",
        "DSI_TX_D0_P": "MIPI_DPHY_DSI_TX_D0P", "DSI_TX_D0_N": "MIPI_DPHY_DSI_TX_D0N",
        "DSI_TX_D1_P": "MIPI_DPHY_DSI_TX_D1P", "DSI_TX_D1_N": "MIPI_DPHY_DSI_TX_D1N",
        "DSI_TX_D2_P": "MIPI_DPHY_DSI_TX_D2P", "DSI_TX_D2_N": "MIPI_DPHY_DSI_TX_D2N",
        "DSI_TX_D3_P": "MIPI_DPHY_DSI_TX_D3P", "DSI_TX_D3_N": "MIPI_DPHY_DSI_TX_D3N",
        "CSI_D0_CK_P": "MIPI_DPHY_CSI0_RX_CLKP", "CSI_D0_CK_N": "MIPI_DPHY_CSI0_RX_CLKN",
        "CSI_D0_D0_P": "MIPI_DPHY_CSI0_RX_D0P", "CSI_D0_D0_N": "MIPI_DPHY_CSI0_RX_D0N",
        "CSI_D0_D1_P": "MIPI_DPHY_CSI0_RX_D1P", "CSI_D0_D1_N": "MIPI_DPHY_CSI0_RX_D1N",
        "CSI_D0_D2_P": "MIPI_DPHY_CSI0_RX_D2P", "CSI_D0_D2_N": "MIPI_DPHY_CSI0_RX_D2N",
        "CSI_D0_D3_P": "MIPI_DPHY_CSI0_RX_D3P", "CSI_D0_D3_N": "MIPI_DPHY_CSI0_RX_D3N",
        "USB_D_P": "USB_DRD0_DP", "USB_D_N": "USB_DRD0_DM",
        "USB_VBUS_DET": "USB_DRD0_VBUSDET",
    }

    # pinctrl 信号名 → 项目信号的匹配规则 (按功能关键词)
    MUX_HINT = {
        "I2C_A_SCL": ["i2c0_scl", "i2c1_scl"], "I2C_A_SDA": ["i2c0_sda", "i2c1_sda"],
        "I2C_B_SCL": ["i2c2_scl", "i2c3_scl"], "I2C_B_SDA": ["i2c2_sda", "i2c3_sda"],
        "SPI_SCLK": ["spi0_clk", "fspi0_clk"], "SPI_MOSI": ["spi0_d0", "fspi0_d0"],
        "SPI_MISO": ["spi0_d1", "fspi0_d1"], "SPI_CSn": ["spi0_csn0", "fspi0_csn0"],
        "UART_TX": ["uart2_tx", "uart0_tx"], "UART_RX": ["uart2_rx", "uart0_rx"],
        "JTAG_TCK": ["jtag_tck"], "JTAG_TMS": ["jtag_tms"],
        "JTAG_TDI": ["jtag_tdi"], "JTAG_TDO": ["jtag_tdo"],
        "PWR_CTRL": ["pwr_ctrl"], "BOOT_N": ["boot"], "RESET_N": ["reset"],
        "XTAL_IN": ["osc24m", "osc25m", "xtal"], "XTAL_OUT": ["osc24m", "osc25m", "xtal"],
        "FSIN": ["fsin"], "BAT_DET": ["saradc"], "KEY_VOL_P": ["key"], "KEY_VOL_M": ["key"],
        "KEY_PWR": ["key"], "KEY_CAM": ["key"], "LED_R": ["led"], "LED_G": ["led"], "LED_B": ["led"],
        "ID0": ["id"], "ID1": ["id"], "CSI_MCLK": ["cam_clk"], "CSI_RESET_N": ["csi_rst"],
    }

    rows = []
    for sig in PROJECT_SIGNALS:
        rec = {"signal": sig, "kind": "", "ball": "", "gpio": "", "mux": "",
               "datasheet_func": "", "pinctrl_sig": "", "evidence": "", "note": ""}
        if sig in FIXED:
            fn = FIXED[sig]
            p = ball_by_func.get(fn)
            rec.update(kind="固定功能脚", ball=(p or {}).get("ball", "?"),
                       gpio=(p or {}).get("gpio", ""), datasheet_func=fn,
                       evidence="[官方] Datasheet V1.1 §2.6",
                       note="★固定功能脚, 不是 pinctrl 复用 ⇒ 无 mux 概念")
            rows.append(rec)
            continue
        # pinctrl 路径
        cands = None
        for h in MUX_HINT.get(sig, []):
            hits = []
            for name, pins_ in pinctrl.items():
                if h in name:
                    hits += [(name, x) for x in pins_]
            if hits:
                cands = hits
                break
        if cands:
            best = None
            for name, x in cands:
                g = gpio_name(x["bank"], x["pin"]).upper()
                p = gpio_to_ball.get(g)
                if p:
                    best = (name, x, p)
                    break
            if best:
                name, x, p = best
                rec.update(kind="pinctrl 复用脚", ball=p["ball"], gpio=gpio_name(x["bank"], x["pin"]),
                           mux=str(x["mux"]), pinctrl_sig=name,
                           evidence="[官方] BSP dtsi + Datasheet §2.6",
                           note=f"mux={x['mux']} (dtsi 里 &pcfg_* 之外的复用值)")
                rows.append(rec)
                continue
        rec.update(kind="未找到", evidence="[0数据]",
                   note="★datasheet 与 pinctrl 两层都没直接命中 ⇒ 需人工核 (可能是专用脚或命名不同)")
        rows.append(rec)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hit = sum(1 for r in rows if r["ball"])
    print(f"✅ 引脚分配表: {hit}/{len(rows)} 个项目信号找到球位")
    print(f"   固定功能脚: {sum(1 for r in rows if r['kind']=='固定功能脚')}"
          f" | pinctrl 复用脚: {sum(1 for r in rows if r['kind']=='pinctrl 复用脚')}"
          f" | 未找到: {sum(1 for r in rows if r['kind']=='未找到')}")
    for r in rows:
        if r["kind"] == "未找到":
            print(f"   ⚠️  {r['signal']:14s} → 未找到")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
