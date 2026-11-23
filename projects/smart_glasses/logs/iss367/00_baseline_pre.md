=== ISS-367 baseline (pre-work) ===
date: 2026-11-23T17:53:45+08:00
--- board md5/mtime ---
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800
--- netlist/pins/BOM ---
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
--- target md5 ---
c7945f59ad1af4b299d851fac8590a2a  MECH/BOARD_ONEPASS_MECH_SYNC.md
d7b33ed79a82dfe816107e323d81c8bb  MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md
8a38ac9319e2e47fc080d3651995cf5b  MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md
--- existing gate scripts ---
6141ae7dd7303c280d30562ed6bd11f6  MECH/check_onepass_s10_fp_swap_impact.py
5247486a6739d9b0cd5cf9a886c771e8  MECH/check_onepass_mech_sync.py
4eddd08fa4c1e9894a63b8cba0dee500  MECH/check_onepass_struct_crosscheck.py
d4bd30c241718a8c0baf3084f78e2eb7  MECH/check_board_frame_coords.py
483d018a66d17d2ead25d1558a1f8ffe  MECH/check_demo_struct_truth.py
5f370bb8cf828473e70ccc5d6412da98  state/gate_check.py
c9191025020fefd9b475e2573a335815  state/merge.py
3b383a52b4fa540f1d16a2c6f3811de8  state/frag_write.py
--- frag ---
23262e2f1c4a30162c93b66e5aa59bcf  state/fragments/mech.yaml
