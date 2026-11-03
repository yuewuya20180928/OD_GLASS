#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_netlist_fpc_pins.py —— ★修网表的 FPC 针位缺陷 (2026-11-03 09:3x)

★★ 为什么必须修 (实测证据, 不是推测):
  ① `HW/PCB/FPC_PIN_TABLES.md` 的 **Radxa Camera 4K 31 针表 / Display 40 针表** 是模组原厂定义
  ② 而网表里**同时留着 A1 段之前 (18p/22p 跨铰链版) 的行** ⇒ 同一个连接器脚上挂了 2~4 个不同的网
     ⇒ 板子上就是**短路** (CSI_D0_CK_P 同时在 pin1 与 pin18; CSI_MCLK 同时在 pin11 与 pin20; …)
  ③ 真值表: Radxa Camera 4K 31 针 ⇒ pin15=MDP1 / pin16=GND / pin17=MCN / pin18=MCP / pin12=MDP2
     ⇒ 旧版把 pin15/16/17 当"传感器三条轨"、pin12 当"CSI 复位"、pin18 当"回流地" **全错**
  ④ Display 40 针 ⇒ pin16=GND (旧行重复占用) · pin1=NC (旧声明行占用)

★★ 本脚本只做**外科手术式**改写: 删除指定语句 / 替换指定子串 ⇒ 不动其它逻辑 ⇒
   改完 `ast.parse` 语法自检 + 重跑 gen_netlist.py + 新门禁复算。

用法: python3 state/_patch_netlist_fpc_pins.py [--check]
"""
import ast
import os
import re
import sys

GEN = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/gen_netlist.py'


def stmt_span(src, needle, start=0):
    """找到含 needle 的语句 (按括号配平) 的 (起, 止) 字符区间"""
    i = src.find(needle, start)
    if i < 0:
        raise KeyError(f'needle not found: {needle[:70]}')
    # 回退到语句开头 (行首 + 缩进 + add(/conn_row(/for 等)
    ls = src.rfind('\n', 0, i) + 1
    j = src.find('(', i)
    depth = 0
    k = j
    in_s = None
    while k < len(src):
        ch = src[k]
        if in_s:
            if ch == '\\':
                k += 2
                continue
            if ch == in_s:
                in_s = None
        else:
            if ch in '"\'':
                in_s = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
        k += 1
    end = k + 1
    # 含尾随逗号与换行
    while end < len(src) and src[end] in ',':
        end += 1
    while end < len(src) and src[end] != '\n':
        end += 1
    end += 1
    return ls, end


def delete_stmt(src, needle, why, count=1):
    done = 0
    pos = 0
    for _ in range(count):
        try:
            ls, end = stmt_span(src, needle, pos)
        except KeyError:
            break
        # ★复合语句 (for/if/while/def) ⇒ 连同**缩进体**一起删 (否则留下孤立 body ⇒ IndentationError)
        head = src[ls:end].lstrip()
        if head.startswith(('for ', 'if ', 'while ', 'def ', 'with ')):
            indent = len(src[ls:end]) - len(src[ls:end].lstrip())
            lines = src[end:].split('\n')
            k = 0
            for ln in lines:
                if ln.strip() == '':
                    k += 1
                    continue
                ind = len(ln) - len(ln.lstrip())
                if ind <= indent:
                    break
                k += 1
            end = end + len('\n'.join(lines[:k]))
            if k < len(lines):
                end += 1
        src = src[:ls] + src[end:]
        pos = ls
        done += 1
    print(f'  [删] {done}/{count} × {why}')
    return src, done


def replace(src, old, new, why, expect=1):
    n = src.count(old)
    if n != expect:
        print(f'  ★★[替换失败] {why}: 命中 {n} 处 (期望 {expect}) —— 未改动')
        return src, False
    src = src.replace(old, new)
    print(f'  [替] {why} ({n} 处)')
    return src, True


def main():
    src = open(GEN, encoding='utf-8').read()
    orig = src
    print('=== 1. 连接器"声明行"不再占用任何针脚 ===')
    src, _ = replace(src,
                     'add("P4", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT pin1", "CONN_LIGHT",',
                     'add("P4", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT",',
                     'CONN_LIGHT 声明行')
    src, _ = replace(src,
                     'add("P5", "CONN_CAM", "CONN_CAM", "CONN_CAM pin1", "CONN_CAM",',
                     'add("P5", "CONN_CAM", "CONN_CAM", "CONN_CAM", "CONN_CAM",',
                     'CONN_CAM 声明行')
    src, _ = replace(src,
                     'add("P1", "BAT_CHG", "J_CHG", "J_CHG pin1", "J_CHG",',
                     'add("P1", "BAT_CHG", "J_CHG", "J_CHG", "J_CHG",',
                     'J_CHG 声明行')
    src, _ = replace(src,
                     'add("P6", "CONN_USB", "CONN_USB", "CONN_USB pin1", "CONN_USB",',
                     'add("P6", "CONN_USB", "CONN_USB", "CONN_USB", "CONN_USB",',
                     'CONN_USB 声明行')
    src, _ = replace(src,
                     'add("P8", "J_DEBUG", "J_DEBUG", "J_DEBUG pin1", "J_DEBUG",',
                     'add("P8", "J_DEBUG", "J_DEBUG", "J_DEBUG", "J_DEBUG",',
                     'J_DEBUG 声明行')

    print('=== 2. 删掉 A1 段之前的陈旧行 (跨铰链 18p 版 / 传感器芯片级轨 / 重复 GND 脚) ===')
    src, _ = delete_stmt(src, 'conn_row(by_id, "A-12", "P5", "CSI_RESET_N"',
                          'CSI_RESET_N 的 SoC 侧行 (复位真值 = pin27)')
    src, _ = delete_stmt(src, 'add("P5", "VDD_1V8_IO", "R_PU_CSI_RST"',
                          'R_PU_CSI_RST 上拉电阻')
    src, _ = delete_stmt(src, 'add("P5", "CSI_RESET_N", "CONN_CAM pin12"',
                          'CSI_RESET_N → CONN_CAM pin12 (pin12 其实是 MDP2!)')
    src, _ = delete_stmt(src, 'for rail, pin in (("SENSOR_AVDD", 15)',
                          'sensor 三条轨接 pin15/16/17 (pin15=MDP1/16=GND/17=MCN!)')
    src, _ = delete_stmt(src, 'add("P5", "GND", "CONN_CAM pin18"',
                          'GND → CONN_CAM pin18 (pin18 其实是 MCP!)')
    src, _ = delete_stmt(src, 'add("P9", "HINGE_CSI", "CONN_CAM"',
                          'HINGE_CSI 跨铰链 camera 通道 (11-02 19:25 已改板内 FPC 座)')
    src, _ = delete_stmt(src, 'add("P4", "GND", "CONN_LIGHT pin16"',
                          'GND → CONN_LIGHT pin16 (与 40 针表 pin16=GND 重复)')
    src, _ = delete_stmt(src, 'add("P9", "HINGE_DSI", "CONN_LIGHT"',
                          'HINGE_DSI 跨铰链 display 通道 (同上)')

    print('=== 3. ESD 阵列挂到 CSI 时钟正脚 (pin18=MCP), 不是 pin1 ===')
    src, _ = replace(src,
                     'add("P9", "CSI_D0_CK_P", "CONN_CAM pin1", "D_ESD_CAM", "D_ESD_CAM",',
                     'add("P9", "CSI_D0_CK_P", "CONN_CAM pin18", "D_ESD_CAM", "D_ESD_CAM",',
                     'D_ESD_CAM 挂点')

    print('=== 4. 测试点改挂到真实针脚 (31/40 针表) ===')
    TP_FIX = [
        ('("TP_SENSOR_2V8", "SENSOR_AVDD", "CONN_CAM pin15"', None),
        ('("TP_SENSOR_IO2V8", "SENSOR_VDD_IO", "CONN_CAM pin16"', None),
        ('("TP_SENSOR_1V2", "SENSOR_CORE", "CONN_CAM pin17"', None),
        ('("TP_CSI_CK_P", "CSI_D0_CK_P", "CONN_CAM pin1"', 'CONN_CAM pin18'),
        ('("TP_CSI_CK_N", "CSI_D0_CK_N", "CONN_CAM pin2"', 'CONN_CAM pin17'),
        ('("TP_CSI_D0_P", "CSI_D0_D0_P", "CONN_CAM pin3"', 'CONN_CAM pin15'),
        ('("TP_CSI_D0_N", "CSI_D0_D0_N", "CONN_CAM pin4"', 'CONN_CAM pin14'),
        ('("TP_CSI_RST", "CSI_RESET_N", "CONN_CAM pin12"', None),
        ('("TP_MCLK", "CSI_MCLK", "CONN_CAM pin11"', 'CONN_CAM pin20'),
        ('("TP_DSI_CK_P", "DSI_D0_CK_P", "CONN_LIGHT pin1"', 'CONN_LIGHT pin15'),
        ('("TP_DSI_CK_N", "DSI_D0_CK_N", "CONN_LIGHT pin2"', 'CONN_LIGHT pin14'),
        ('("TP_DSI_D0_P", "DSI_D0_D0_P", "CONN_LIGHT pin3"', 'CONN_LIGHT pin9'),
        ('("TP_DSI_D0_N", "DSI_D0_D0_N", "CONN_LIGHT pin4"', 'CONN_LIGHT pin8'),
        ('("TP_I2CA_SCL", "I2C_A_SCL", "CONN_CAM pin13"', 'CONN_CAM pin24'),
        ('("TP_I2CA_SDA", "I2C_A_SDA", "CONN_CAM pin14"', 'CONN_CAM pin25'),
        ('("TP_I2CB_SCL", "I2C_B_SCL", "CONN_LIGHT pin11"', 'CONN_LIGHT pin28'),
        ('("TP_I2CB_SDA", "I2C_B_SDA", "CONN_LIGHT pin12"', 'CONN_LIGHT pin27'),
    ]
    for old, new in TP_FIX:
        if new is None:
            src, _ = delete_stmt(src, old, f'删除测试点 {old[:28]}')
        else:
            src, _ = replace(src, old, old.replace(old.split('"')[-2], new)
                             if False else old[:old.rfind('"')] + new + '"',
                             f'测试点改挂 {new}')

    print('=== 5. 说明文字订正 (声明行不再占脚) ===')
    src, _ = replace(src,
                     '"[CONN_CAM] 主 PCB ↔ sensor 板 40p 跨铰链连接器; pin1/2=CSI_CK, 3..10=CSI_D0..D3, "',
                     '"[CONN_CAM] ★**2026-11-03 09:3x 订正**: 本行**不再占用任何针脚** (原占 pin1 ⇒ 与 31 针表 pin1=GND 撞车); "',
                     'CONN_CAM 注释')
    src, _ = replace(src,
                     '"[CONN_CAM] 主 PCB ↔ sensor 板 40p 跨铰链连接器; pin1/2=CSI_CK, 3..10=CSI_D0..D3, "\n'
                     '        "11=MCLK, 12=CSI_RESET_N, 13/14=I2C_A, 15/16/17=sensor 3V3/1V8/2V8; "\n'
                     '        "pin 数/pitch/翻盖方式待结构总工 (ISS-065); ★pin 编号为**本版自拟**, 非规格给定")',
                     '"[CONN_CAM] 针脚分配一律以 `HW/PCB/FPC_PIN_TABLES.md` 的 **Radxa Camera 4K 31 针表** 为准: "\n'
                     '        "1=GND 2/3=MDN4/MDP4 5/6=MDN3/MDP3 11/12=MDN2/MDP2 14/15=MDN1/MDP1 17/18=MCN/MCP "\n'
                     '        "20=MCLK 24/25=SCL/SDA 27=RESET 28/29=VCC3.3V 30/31=VCC5V, 其余 GND/NC")',
                     'CONN_CAM 注释体')

    ast.parse(src)
    if src == orig:
        print('\n★★ 无改动 —— 不落盘')
        return 1
    open(GEN, 'w', encoding='utf-8').write(src)
    print(f'\n✅ 已落盘 {GEN} (语法自检通过)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
