> ★**这是脱敏版** —— 供另一台主机参考拓扑用; ★**真值在旧主机本地, 走带外通道传** (见 `config/OFFLINE_TRANSFER_CHECKLIST.md`)。
> 脱敏项: 板子 SSH 口令 / 内网 IP / 板子用户名 / 本地板端路径 / 板卡型号名。

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → <LAN_IP>, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## SSH Hosts

### 板端 Radxa Cubie A7S (Allwinner A733 NPU)

- **IP**: `<LAN_IP>` (LAN enp4s0, ping 0.4ms, **DHCP 会换 IP**, 8-17 实测从 .3 换到 .5)
  - **铁律**: 每次新会话 SSH 前先 `getent hosts <BOARD_HOSTNAME>.local` 确认当前 IP, 别用写死的
  - ping 失败但 ARP REACHABLE = stale ARP cache, 真 IP 在 mDNS, 别误判板子挂
- **OS**: Debian trixie, kernel `6.6.98-3-aw2511`
- **SSH 用户**: `<BOARD_USER>`
- **SSH 密码**: `<BOARD_SSH_PASSWORD>` （2026-08-05 老板确认）
- **认证方式**: password only, **publickey 失效** (8-03 23:35 已确认)
- **调用方式**: `sshpass -p '<BOARD_SSH_PASSWORD>' ssh -o StrictHostKeyChecking=no <BOARD_VENDOR>@<LAN_IP> '<cmd>'`
- **架构**: aarch64, 8 核
- **NPU**: VIPLite v2.0.3.x (driver Oct 2025 / userspace May 2025/2024，ABI 不匹配详 MEMORY)
- **设备**: 
  - `/dev/video0` USB Microdia UVC 摄像头（640x480 YUYV）
  - `/dev/video1-5` 其他 USB 摄像头/虚拟
  - `/dev/vipcore` NPU 设备
- **模型**: `/etc/npu/yolov5/model/yolov5.nb` (5MB, 7-21 装)
- **A+B .so**: `/home/<BOARD_USER>/od_api/lib/libod_helper.so` (79KB, 8-03 16:15 重编)
- **v24 推流脚本**: `/home/<BOARD_USER>/camera_uvc_od_pipeline_v24_udpsink.py`
- **v24 log**: `/tmp/v24.log`

---

## 板端当前稳态（2026-08-05 00:30 实测）

- v24 推流 PID 1497 / 1514 / 1515 在跑
- 稳态 FPS: **10.34**（dets=[none], 摄像头前没东西）
- worker_total_ms: 79.9ms
- vip_run_network: 27ms (NPU 硬件)
- tensor_to_fp memcpy: 41ms (3 段 26MB + 6.5MB + 1.6MB)
- awnn_run total: 67.7ms
- worker_post_ms: 10.9ms

## Related

- [Agent workspace](/concepts/agent-workspace)
