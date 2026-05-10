# 高岸ERP系统-IoT技术实施与家庭测试方案

**文档编号**：IOT-02  
**版本**：V1.0  
**日期**：2026年5月5日  
**状态**：草稿  
**关联文档**：IOT-01（设备采购与安装清单）、ARC-01（技术架构设计）  
**编制依据**：盈隆店IoT设备清单、三层架构设计（控制层/通信层/设备层）

---

## 一、文档目的

本文档为盈隆店IoT系统的技术落地实施方案，覆盖从家庭测试环境搭建到现场部署的全过程。由于盈隆店场地尚未完工，先在家庭环境搭建完整技术栈进行验证，设备到位后按配置直接部署到门店。

**核心理念**：IoT层与ERP业务层解耦。设备装好、HA跑通后，业务规则就是配置项，不依赖软件需求评审结果。

---

## 二、整体技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **控制层** | Home Assistant（Docker部署） | 核心自动化引擎，跑在M720q上 |
| **通信层 - 无线** | Zigbee2MQTT → Mosquitto MQTT | Zigbee设备接入，统一MQTT总线 |
| **通信层 - 有线** | Modbus TCP（RS485主控） | 灯光面板、继电器模块 |
| **通信层 - 音视频** | DSP HTTP API / 蓝牙音频 | 音源切换、分区控制 |
| **网络层** | OpenWRT（NanoPi R5S） | VLAN隔离、防火墙、Tailscale VPN |
| **存储层** | NVR（4路+4TB） | 摄像头录像30天循环 |

---

## 三、家庭测试环境搭建

### 3.1 硬件清单（家庭测试用）

盈隆店正式设备未到货前，先用同类或替代设备验证技术方案：

| 设备 | 家庭测试用 | 验证目的 |
|------|-----------|---------|
| HA主机（M720q） | 同（正式设备） | HA部署、Docker运行稳定性 |
| 软路由（R5S） | 同（正式设备） | VLAN划分、防火墙规则、Tailscale |
| PoE交换机 | 同（正式设备） | VLAN端口分配、PoE供电 |
| Zigbee网关（Sonoff） | 同（正式设备） | Zigbee2MQTT接入、信号覆盖测试 |
| RS485主控制器 | 同（正式设备） | Modbus TCP总线通信 |
| 智能门锁 | 1把（通通锁） | Zigbee接入、动态密码、门磁检测 |
| 智能灯光面板 | 2个（RS485） | 手拉手总线串联、HA调光控制 |
| 毫米波雷达 | 1个（HLK-LD2410D） | 人体存在检测、无人超时告警 |
| 温湿度传感器 | 1个（Zigbee） | 数据上报、联动规则 |
| 吸顶音箱 | 2只 | 定压音箱+DSP分区测试（可选） |
| 蓝牙接收模块 | 1个（CSR8675） | 蓝牙配对、DSP音源切换 |
| PoE摄像头 | 1个（海康威视） | ONVIF接入NVR、HA集成 |

### 3.2 网络拓扑（家庭测试）

```
互联网 — 光猫 — NanoPi R5S（OpenWRT）
                    │
                    ├─ VLAN 10（设备/管理）192.168.10.0/24
                    │     ├─ M720q（HA主机）
                    │     ├─ PoE交换机（管理口）
                    │     ├─ RS485主控制器
                    │     └─ NVR
                    │
                    ├─ VLAN 20（客人WiFi）192.168.20.0/24
                    │     └─ AP（客人SSID）
                    │
                    └─ VLAN 10（PoE设备，通过交换机）
                          ├─ Zigbee网关
                          ├─ PoE摄像头
                          └─ AP（管理SSID）
```

### 3.3 测试计划

| 阶段 | 内容 | 验证标准 | 预计耗时 |
|------|------|---------|---------|
| **P1 网络基础** | OpenWRT刷机+VLAN划分+WiFi配置 | VLAN间隔离生效，设备互通 | 1天 |
| **P2 HA核心** | Docker部署HA+Ping检查+Z2M安装 | HA Web UI可达，Zigbee网关在线 | 1天 |
| **P3 Zigbee设备** | 门锁+传感器+雷达配对 | 实体正确上报状态 | 2天 |
| **P4 RS485总线** | 灯光面板+继电器模块接入 | Modbus TP读写正常 | 2天 |
| **P5 自动化规则** | 欢迎/退房/节能场景 | 规则触发正确执行 | 2天 |
| **P6 音视频** | DSP+蓝牙+音箱接入 | 分区控制、音源切换 | 2天 |
| **P7 安防** | 摄像头+NVR+门锁告警 | 录像存储、告警推送 | 1天 |
| **P8 集成联调** | 全链路闭环测试 | 预约→开门→场景→退房 | 2天 |

---

## 四、HA部署规范

### 4.1 系统环境

| 项目 | 配置 |
|------|------|
| 主机 | 联想M720q（i5-8500T, 8GB RAM, 256GB SSD） |
| 操作系统 | Debian 12（最小安装） |
| 容器引擎 | Docker CE + Docker Compose |
| 存储分区 | `/opt/ha`（HA配置持久化） |

### 4.2 Docker Compose 配置

```yaml
version: '3.8'
services:
  homeassistant:
    container_name: ha
    image: ghcr.io/home-assistant/home-assistant:stable
    restart: unless-stopped
    network_mode: host
    volumes:
      - /opt/ha/config:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=Asia/Shanghai

  mosquitto:
    container_name: mqtt
    image: eclipse-mosquitto:2
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - /opt/mosquitto/config:/mosquitto/config
      - /opt/mosquitto/data:/mosquitto/data

  zigbee2mqtt:
    container_name: z2m
    image: koenkk/zigbee2mqtt:latest
    restart: unless-stopped
    devices:
      - /dev/ttyACM0:/dev/ttyACM0
    volumes:
      - /opt/z2m/data:/app/data
    environment:
      - TZ=Asia/Shanghai
```

### 4.3 Zigbee2MQTT 配置要点

```yaml
# /opt/z2m/data/configuration.yaml
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://192.168.10.2:1883

serial:
  port: /dev/ttyACM0
  adapter: zstack

advanced:
  network_key: GENERATE_AUTO
  pan_id: GENERATE_AUTO
  channel: 15
  log_level: info

device_options:
  legacy: false  # 使用新版MQTT消息格式
```

**信道选择说明**：Zigbee（信道15）与WiFi 2.4GHz（信道1/6/11）错开，避免同频干扰。

### 4.4 设备命名规范

HA实体命名规则：

```
实体ID格式：<domain>.<区域>_<设备类型>_<序号>
示例：
  lock.das_room_door         # 大会议室门锁
  light.tearoom_a_main       # 中茶室A主灯
  sensor.hall_temperature    # 展厅温湿度
  binary_sensor.hall_radar   # 展厅毫米波雷达

MQTT Topic格式：
  zigbee2mqtt/<设备IEEE地址>  # Zigbee设备状态
  modbus/<设备ID>/<寄存器>    # Modbus设备
  ha/场景/触发器              # 场景事件
```

---

## 五、RS485总线方案

### 5.1 拓扑结构

```
RS485主控制器（配电箱内，Modbus TCP转RS485）
    │
    ├── 大会议室：RS485继电器模块（2路：灯光+排风）
    │
    ├── 中茶室A：RS485继电器模块（2路：灯光+排风）
    │
    ├── 中茶室B：RS485继电器模块（2路：灯光+排风）
    │
    └── 大茶室C：RS485继电器模块（2路：灯光+排风）
```

### 5.2 技术参数

| 项目 | 参数 |
|------|------|
| 总线类型 | 2芯屏蔽双绞线 |
| 通信协议 | Modbus RTU（9600bps, 8N1） |
| 终端电阻 | 总线两端各120Ω |
| 最大长度 | ≤100m（实际约30m） |
| 设备地址 | 每个继电器模块独立地址（1-4） |

### 5.3 HA集成

通过Modbus TCP集成，在HA的`configuration.yaml`中添加：

```yaml
modbus:
  - name: hub
    type: tcp
    host: 192.168.10.10
    port: 502

switch:
  - platform: modbus
    name: "大会议室灯光"
    hub: hub
    slave: 1
    register: 0
    command_on: 0xFF00
    command_off: 0x0000
  
  - platform: modbus
    name: "大会议室排风"
    hub: hub
    slave: 1
    register: 1
    command_on: 0xFF00
    command_off: 0x0000
```

---

## 六、自动化规则模板

### 6.1 HA自动化规则（YAML）

**欢迎场景**：客人开锁→联动设备

```yaml
alias: "场景 - 欢迎客人（大会议室示例）"
trigger:
  - platform: state
    entity_id: lock.das_room_door
    to: "unlocked"
condition:
  - condition: state
    entity_id: input_boolean.room_booked
    state: "on"
action:
  - service: light.turn_on
    target:
      entity_id: light.das_room_main
    data:
      brightness: 200
  
  - service: cover.open_cover
    target:
      entity_id: cover.das_room_curtain

  - service: media_player.select_source
    target:
      entity_id: media_player.zone2
    data:
      source: "背景音乐"

  - delay:
      seconds: 2
  
  - service: tts.cloud_say
    target:
      entity_id: media_player.zone2
    data:
      message: "欢迎光临高岸茶室，祝您使用愉快"
  
mode: single
```

**退房场景**：系统通知→关闭设备

```yaml
alias: "场景 - 退房关设备"
trigger:
  - platform: webhook
    webhook_id: checkout_trigger
condition: []
action:
  - service: light.turn_off
    target:
      entity_id: "{{ trigger.json.room_light_entities }}"
  
  - service: cover.close_cover
    target:
      entity_id: "{{ trigger.json.room_curtain }}"

  - service: media_player.media_stop
    target:
      entity_id: "{{ trigger.json.room_player }}"

  - service: climate.turn_off
    target:
      entity_id: "{{ trigger.json.room_ac }}"

  - service: lock.lock
    target:
      entity_id: "{{ trigger.json.room_lock }}"

mode: single
```

**节能场景**：雷达无人超时告警

```yaml
alias: "告警 - 无人超时（中茶室A示例）"
trigger:
  - platform: state
    entity_id: binary_sensor.tearoom_a_radar
    to: "off"
    for:
      minutes: 30
condition:
  - condition: state
    entity_id: lock.tearoom_a_door
    state: "locked"
  - condition: state
    entity_id: input_boolean.tearoom_a_active
    state: "on"
action:
  - service: notify.mobile_app_shop
    data:
      title: "⚠️ 中茶室A无人超时"
      message: "设备已关闭30分钟但房间仍标记为使用中，请确认是否需要退房"
  - service: light.turn_off
    target:
      entity_id: light.tearoom_a_main
  - service: climate.turn_off
    target:
      entity_id: climate.tearoom_a_ac

mode: single
```

**门锁低电量告警**

```yaml
alias: "告警 - 门锁低电量"
trigger:
  - platform: numeric_state
    entity_id: sensor.das_room_battery
    below: 20
condition: []
action:
  - service: notify.mobile_app_shop
    data:
      title: "🔋 大会议室门锁低电量"
      message: "当前电量 {{ trigger.to_state.state }}%，请尽快更换电池"

mode: single
```

**蓝牙音源自动切换**

```yaml
alias: "音频 - 蓝牙切换（中茶室A）"
trigger:
  - platform: mqtt
    topic: "bluetooth/tearoom_a/connection"
condition:
  - condition: template
    value_template: "{{ 'connect' in trigger.payload }}"
action:
  - service: media_player.select_source
    target:
      entity_id: media_player.zone3
    data:
      source: "蓝牙音频"

mode: single
```

**空调预冷/预热**

```yaml
alias: "节能 - 预约预冷（中茶室A示例）"
trigger:
  - platform: time
    at: "trigger_time"  # 由ERP系统预约提前5分钟触发
condition:
  - condition: template
    value_template: "{{ states('sensor.tearoom_a_temperature') | float > 28 }}"
action:
  - service: climate.turn_on
    target:
      entity_id: climate.tearoom_a_ac
    data:
      temperature: 24
      hvac_mode: cool

mode: single
```

### 6.2 场景模板（HA场景文件）

HA场景配置模板按房间类型定义，新房间上线时只需拷贝模板并替换实体ID：

```
# 场景模板目录结构
/opt/ha/scenes/
  ├── templates/
  │   ├── welcome_room.yaml         # 欢迎场景模板
  │   ├── checkout_room.yaml        # 退房场景模板
  │   ├── energy_save.yaml          # 节能场景模板
  │   └── audio_bluetooth.yaml      # 蓝牙切换模板
  └── active/
      ├── das_room_scenes.yaml      # 大会议室实例
      ├── tearoom_a_scenes.yaml     # 中茶室A实例
      ├── tearoom_b_scenes.yaml     # 中茶室B实例
      └── tearoom_c_scenes.yaml     # 大茶室C实例
```

---

## 七、VRF空调控制方案

### 7.1 前提条件

- 盈隆店空调品牌/型号待确认
- 中弘VRF网关兼容品牌：大金、日立、三菱、美的、格力、海尔等主流品牌
- 采购前必须确认空调室外机型号与网关兼容

### 7.2 集成方式

通过中弘VRF网关的RS485接口直连空调总线：

```
空调室外机 ←RS485→ 中弘VRF网关 ←Modbus TCP→ HA
```

### 7.3 备选方案

如VRF网关不兼容，降级为红外遥控方案：

```
HA → 红外发射器（BroadLink RM4 Pro）→ 空调室内机
```

红外方案功能受限（无法获取室内温度、无法精确设温），仅作备选。

---

## 八、音频分区与DSP配置

### 8.1 DSP矩阵路由

| 输入通道 | 音源 | 输出分区 |
|---------|------|---------|
| IN1 | HA背景音乐（USB播放器） | 1区（展厅）、3/4/5区（茶室默认） |
| IN2 | 电视音频（HDMI分离） | 2区（大会议室） |
| IN3 | 蓝牙接收模块（大会议室） | 2区（K歌模式） |
| IN4 | 茶室蓝牙模块（混合信号） | 3/4/5区（蓝牙配对时切换） |

### 8.2 定压功放分区

功放5个分区对应DSP的5路输出：
- 200W总功率，展厅2只音箱（60W）+大会议室4只（120W）+茶室各1只（20W）≈ 200W
- 各分区独立音量调节

---

## 九、供电与可靠性

### 9.1 UPS供电策略

| 设备 | 保障时长 | 说明 |
|------|---------|------|
| R5S软路由 | ≥30min | UPS直供 |
| PoE交换机 | ≥30min | UPS直供 |
| HA主机（M720q） | ≥30min | UPS直供 |
| NVR | ≥30min | UPS直供 |
| RS485主控制器 | ≥30min | 配电箱取电（同回路UPS） |
| Zigbee网关 | ≥30min | 交换机PoE供电 |
| 门锁 | 续航≥1年 | 自带电池，低电量告警 |
| DSP/功放 | 无UPS | 音频非关键业务，市电直供 |

### 9.2 离线容错

- 门锁支持离线动态密码，HA或网络故障不影响客人开门
- RS485灯光控制为物理常通型，故障时墙壁物理开关仍可用
- HA通过MQTT retain消息保持设备最后状态
- 关键自动化规则写入HA本地存储，断网后继续执行

---

## 十、安全与权限

### 10.1 VLAN防火墙规则

```
VLAN 20（客人WiFi）→ VLAN 10（设备）：全部禁止
VLAN 10 → VLAN 20：禁止主动发起
VLAN 10 内部：放行必要服务（MQTT 1883, Modbus 502, HTTP 8123）
AP客户端隔离：同SSID下禁止互访
```

### 10.2 HA安全配置

```
- HTTP → HTTPS重定向（自签名证书或Let's Encrypt）
- 仅VLAN 10可访问HA Web UI（8123端口）
- 外网访问通过Tailscale VPN（不进VLAN 20）
- 门锁动态密码由HA Gateway模块管理，不与客人直接通信
```

### 10.3 远程访问

Tailscale VPN组网：

```
广州家里（家庭测试环境）
  │
  └── Tailscale ── 盈隆店（正式环境）
       │
  └── 开发者远程维护
```

HA主机安装Tailscale，映射8123端口，开发者和总部管理员通过Tailscale IP访问。

---

## 十一、家庭测试验收标准

各阶段测试完成后，填写以下检查表：

| 检查项 | 通过条件 | 状态 |
|--------|---------|------|
| HA主机Docker运行 | `docker ps` 显示3个容器正常运行 | □ |
| MQTT通信 | MQTT Explorer可看到设备Topic | □ |
| Zigbee网关 | Zigbee2MQTT显示Permit Join状态 | □ |
| 门锁配对 | 门锁状态实时显示在HA | □ |
| 毫米波雷达 | 有人/无人状态正确切换 | □ |
| 温湿度传感器 | 数据正常上报 | □ |
| RS485灯光控制 | HA可开关/调光 | □ |
| Modbus总线 | 继电器模块正常响应 | □ |
| 摄像头/NVR | 实时画面+录像回放可用 | □ |
| 蓝牙音频 | DSP通道切换正常 | □ |
| 欢迎场景 | 开锁→亮灯→播放欢迎语 | □ |
| 退房场景 | 一键关所有设备 | □ |
| 无人超时告警 | 30分钟无人触发推送 | □ |
| VLAN隔离 | 客人WiFi无法访问设备网 | □ |
| Tailscale远程 | 外部可访问HA Web UI | □ |

---

## 十二、后续工作

1. **采购家庭测试设备** — 按3.1清单采购最少必要设备（先买M720q+R5S+PoE交换机+Zigbee网关）
2. **M720q装机** — 安装Debian 12+Docker，部署HA全家桶
3. **OpenWRT刷机** — NanoPi R5S刷 FriendlyWrt，配置VLAN
4. **逐项测试** — 按3.3测试计划推进，每项通过后确认
5. **整理安装笔记** — 测试过程中记录的问题和解决方案，作为正式部署的操作手册

---

## 附录：关联文档

| 文档编号 | 文档名称 | 关系 |
|---------|---------|------|
| IOT-01 | 物联网设备采购与安装清单（盈隆店专版） | 设备清单和安装要求 |
| ARC-01 | 系统技术架构设计 | 整体技术架构 |
| — | HA配置手册（待编写） | 家庭测试完成后整理 |
| — | 盈隆店部署操作手册（待编写） | 正式部署前编写 |
