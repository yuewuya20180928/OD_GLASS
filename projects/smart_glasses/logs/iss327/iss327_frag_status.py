#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_frag_status.py —— ISS-327 cont1 · 只更新分片 status 段 (★走 state/frag_write.py 的原子写★)
★为什么单独一个脚本: ★追加 artifacts/needs/claims 会重复⇒ 只能单独刷 status.summary★
"""
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

SUMMARY = (
    "★ISS-327 (2026-11-18 14:5x~17:0x · cont1 事故后重做) 交卷: 「板那一趟」当天 SW 侧改名后闸链复活验证。核心读数: "
    "① 「重建注册表」【既不是必要条件也不是充分条件】—— 实测【SW 文档与板同批改名 ⇒ check_sw_ref_reachability 用【旧注册表】就已经 rc=0 "
    "(OK 78 / DRIFT 0 / MISSING 3 ⇒ 与基线逐字相同)】; 而【文档没同批改名时重建 ⇒ 58 条漂移/假红被洗成 56 条真隐患/真红 ⇒ 一样红·红得更凶】; "
    "② 「--freeze-registry」【自己】不会把真隐患洗白 —— 3 条反向用例 (建闸日那 3 条真隐患各改成【全大写·从来不存在过的新位号形状】) "
    "⇒ 重建后【全部仍被 C14 抓住】(MISSING 4 > 上限 3 ⇒ 仍红); ★★但【幽灵 token 的形状】决定抓不抓得住: 含小写(C7)/以 _ 结尾(C8)/SW_ 前缀(C13)/"
    "本身 live(C1) 的四种形状【会被提前吃掉 ⇒ 真的被洗白】⇒ 「真隐患永远不会被洗白」这句话不对★; "
    "③ 改名后仍红 7 道闸【没有一道是注册表能修的】(4 道归板 md5/台账链重锚·1 道归闸脚本位号解析层·1 道连带·3 道 R6 selftest 归夹具·非改名特有); "
    "④ 沙盒纪律升级为零软链 (tar 解包 + 写前 assert not islink + 9 棵沙盒 find -type l 全 = 0 + 对照组 sbCtl 10 道闸 rc 与基线逐字相同 "
    "⇒ 沙盒不引入假红) ⇒ 本单的读数被一个并行兄弟 job 的另一套沙盒【逐字复算一致】; "
    "⑤ 交卷物: SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md (§0~§7 全填·占位符 0) + logs/iss327/02_postrename_gate_table.md (三列 + 对照臂 + 反向用例) "
    "+ logs/iss327/ (机器原始输出) + 交卷单 B0~B8。★【撞车处置】★: 主交付物与读数表曾被一个并行兄弟 job 覆盖 (撞同一路径) ⇒ "
    "本单保留对方内容 + 只做 3 处定点订正 (5 个注入用位号名改写成带反斜杠的形状 ⇒ 否则 ISS-318 闸把本文件自己判成 5 条新增真隐患 ⇒ gate_check rc=1; "
    "SOP §3 表第 2/3 行 rc 2※→1※′ (2※ 是沙盒缺 .bak 备份件的制品); 读数表一个 U+FFFD 乱码字节) ⇒ 闸回绿。边界: 零写板 "
    "(611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17.362193413 逐字节不变) · 零落表 · 真件 SW/tools/*.py 本单一个字节没改 "
    "(开工后真件闸与 SAMEBATCH 清单被兄弟 job 改过·已逐条说明归属·本单用 16:21 之后的版本把全套沙盒重跑一遍 rc 矩阵逐字相同) · "
    "真件 SW/*.md 零改名痕迹 · 只写 state/fragments/sw.yaml 一份分片 · 零外发 · 不替老板拍板 · 不自签 issue_log。交卷前 merge.py+gate_check.py+issue_check.py rc=0 · "
    "Q1 14/18 (★sw-lead 本单 6/6 缺无; 缺的 B2/B3/B4/B5 在 mech-lead 的 ISS-326 交接单里·是占位·本单不越界改别人的交接单★)。"
    "3 条 need 交 main 拍 (重建触发条件 / MISSING 上限机制 / DRIFT 分类语义)。"
)


def main():
    argv = ["python3", "state/frag_write.py", "--agent", "sw-lead",
            "--status", "phase=delivered", "--status", "progress_pct=100",
            "--status", "health=green", "--status", 'summary="%s"' % SUMMARY]
    r = subprocess.run(argv, cwd=PROJ, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr[-2000:])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
