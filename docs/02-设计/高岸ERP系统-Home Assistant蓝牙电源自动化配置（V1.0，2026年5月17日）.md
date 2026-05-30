# 高岸ERP系统-Home Assistant蓝牙电源自动化配置

**版本**：V1.0  
**日期**：2026年5月17日  
**文档状态**：草稿  
**编制依据**：
- 《高岸ERP系统-盈隆店IoT接线实施指南（V1.2）》§6.4
- 方案B音频与控制架构：蓝牙音频模块隐藏安装，继电器CH5控制电源
- RS485继电器模块采用聚英/中盛8路Modbus RTU通讯协议

---

## 1. 概述

本文档提供 Home Assistant 中蓝牙音频模块电源控制的完整配置方案。每个房间的蓝牙音频接收模块（隐藏安装在吊顶电箱内）的DC供电由该房间8路继电器模块的 **CH5** 通道控制。

**控制逻辑闭环**：
- 房间有订单（开单/使用中）→ CH5 ON → 蓝牙模块通电启动 → 客人可搜索并连接蓝牙
- 房间空闲/退单 → CH5 OFF → 蓝牙模块物理断电 → 防止蹭连/串号

---

## 2. Modbus RTU 配置

### 2.1 继电器模块参数

| 参数 | 值 |
|------|-----|
| 设备 | 聚英/中盛 8路继电器模块（Modbus RTU） |
| 通讯 | RS485, 9600 bps, 8N1 |
| Slave ID | 1=大会议室, 2=中茶室A, 3=中茶室B, 4=大茶室C, 5=展厅, 6=工作间 |
| CH5地址 | 保持寄存器（Holding Register）0x0005, 对应第5路继电器 |
| CH5 ON值 | `0xFF00`（线圈吸合） |
| CH5 OFF值 | `0x0000`（线圈释放） |

### 2.2 HA Modbus 集成配置

在 `configuration.yaml` 中添加 Modbus 网关（RS485 通过 USB 转 485 适配器连接）：

```yaml
# configuration.yaml 片段

# ── Modbus RTU (USB转485) ──
modbus:
  - name: "modbus_rs485"
    type: tcp  # 如果通过ser2net或485网关走TCP
    host: 127.0.0.1
    port: 502
  # 如果USB直连HA主机，使用以下配置：
  # type: serial
  # device: /dev/ttyUSB0
  # baudrate: 9600
  # stopbits: 1
  # bytesize: 8
  # parity: N
    delay: 50
    timeout: 3
    retries: 3
```

> 实际部署时根据HA主机连接方式选择 `serial` 或 `tcp`。如使用USB直连且HA运行在容器中，需将USB设备映射到容器内。

---

## 3. HA Packages 配置（推荐方式）

将以下内容保存为 `packages/room_bluetooth_power.yaml`（需在 `configuration.yaml` 中启用 `packages: !include_dir_named packages`）：

```yaml
# ──────────────────────────────────────────────
# packages/room_bluetooth_power.yaml
# 蓝牙音频模块电源控制 — 继电器CH5
# Slave ID: 1=大堂, 2=中A, 3=中B, 4=大C, 5=展厅, 6=工作间
# ──────────────────────────────────────────────

# ── 开关实体 ──
switch:
  # 大会议室 - CH5 蓝牙电源
  - platform: modbus
    name: "BT_Power_RM001"
    hub: modbus_rs485
    slave: 1
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5

  # 中茶室A - CH5 蓝牙电源
  - platform: modbus
    name: "BT_Power_RM002"
    hub: modbus_rs485
    slave: 2
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5

  # 中茶室B - CH5 蓝牙电源
  - platform: modbus
    name: "BT_Power_RM003"
    hub: modbus_rs485
    slave: 3
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5

  # 大茶室C - CH5 蓝牙电源
  - platform: modbus
    name: "BT_Power_RM004"
    hub: modbus_rs485
    slave: 4
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5

  # 展厅 - CH5 蓝牙电源
  - platform: modbus
    name: "BT_Power_RM005"
    hub: modbus_rs485
    slave: 5
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5

  # 工作间 - CH5 蓝牙电源（如有）
  - platform: modbus
    name: "BT_Power_RM006"
    hub: modbus_rs485
    slave: 6
    registers:
      - address: 5
        command_on: 0xFF00
        command_off: 0x0000
    scan_interval: 5


# ── 房间状态辅助传感器 ──
# 这些通过HA REST API或MQTT接收高岸ERP系统的订单状态
# 也可根据 business_sensors 中定义的 binary_sensor 联动
input_boolean:
  room_occupied_rm001:
    name: "大会议室占用状态"
    initial: off
  room_occupied_rm002:
    name: "中茶室A占用状态"
    initial: off
  room_occupied_rm003:
    name: "中茶室B占用状态"
    initial: off
  room_occupied_rm004:
    name: "大茶室C占用状态"
    initial: off
  room_occupied_rm005:
    name: "展厅占用状态"
    initial: off
  room_occupied_rm006:
    name: "工作间占用状态"
    initial: off


# ── 自动化：蓝牙电源随房间状态联动 ──
automation:
  # ── 大会议室 ──
  - id: "bt_power_rm001_on"
    alias: "蓝牙上电 - 大会议室（开单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm001
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bt_power_rm001
      - delay:
          seconds: 5  # 给蓝牙模块稳定上电时间
      - service: system_log.write
        data:
          message: "大会议室 蓝牙模块已上电（CH5 ON）"
          level: info

  - id: "bt_power_rm001_off"
    alias: "蓝牙断电 - 大会议室（退单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm001
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.bt_power_rm001
      - service: system_log.write
        data:
          message: "大会议室 蓝牙模块已断电（CH5 OFF）"
          level: info

  # ── 中茶室A ──
  - id: "bt_power_rm002_on"
    alias: "蓝牙上电 - 中茶室A（开单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm002
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bt_power_rm002
      - delay:
          seconds: 5
      - service: system_log.write
        data:
          message: "中茶室A 蓝牙模块已上电（CH5 ON）"
          level: info

  - id: "bt_power_rm002_off"
    alias: "蓝牙断电 - 中茶室A（退单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm002
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.bt_power_rm002
      - service: system_log.write
        data:
          message: "中茶室A 蓝牙模块已断电（CH5 OFF）"
          level: info

  # ── 中茶室B ──
  - id: "bt_power_rm003_on"
    alias: "蓝牙上电 - 中茶室B（开单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm003
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bt_power_rm003
      - delay:
          seconds: 5
      - service: system_log.write
        data:
          message: "中茶室B 蓝牙模块已上电（CH5 ON）"
          level: info

  - id: "bt_power_rm003_off"
    alias: "蓝牙断电 - 中茶室B（退单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm003
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.bt_power_rm003
      - service: system_log.write
        data:
          message: "中茶室B 蓝牙模块已断电（CH5 OFF）"
          level: info

  # ── 大茶室C ──
  - id: "bt_power_rm004_on"
    alias: "蓝牙上电 - 大茶室C（开单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm004
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bt_power_rm004
      - delay:
          seconds: 5
      - service: system_log.write
        data:
          message: "大茶室C 蓝牙模块已上电（CH5 ON）"
          level: info

  - id: "bt_power_rm004_off"
    alias: "蓝牙断电 - 大茶室C（退单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm004
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.bt_power_rm004
      - service: system_log.write
        data:
          message: "大茶室C 蓝牙模块已断电（CH5 OFF）"
          level: info

  # ── 展厅 ──
  - id: "bt_power_rm005_on"
    alias: "蓝牙上电 - 展厅（开单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm005
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bt_power_rm005
      - delay:
          seconds: 5
      - service: system_log.write
        data:
          message: "展厅 蓝牙模块已上电（CH5 ON）"
          level: info

  - id: "bt_power_rm005_off"
    alias: "蓝牙断电 - 展厅（退单）"
    trigger:
      - platform: state
        entity_id: input_boolean.room_occupied_rm005
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.bt_power_rm005
      - service: system_log.write
        data:
          message: "展厅 蓝牙模块已断电（CH5 OFF）"
          level: info
```

### 3.1 与高岸ERP对接（REST API桥接）

高岸ERP系统通过 REST API 或 MQTT 同步订单状态到 HA。推荐使用 HA REST API 更新 `input_boolean` 状态：

**HA侧**：为每个房间暴露 REST API endpoint：

```yaml
# configuration.yaml 追加
rest_command:
  set_room_occupied:
    url: "http://homeassistant.local:8123/api/states/input_boolean.room_occupied_{{ room }}"
    method: POST
    content_type: "application/json"
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_TOKEN"
    payload: '{"state": "{{ state }}"}'
```

**ERP侧**（伪代码，在订单状态变更时调用）：

```python
# 高岸ERP 订单状态变更回调
def on_order_state_change(room_id, is_active):
    room_map = {
        'RM001': 'rm001',
        'RM002': 'rm002',
        'RM003': 'rm003',
        'RM004': 'rm004',
        'RM005': 'rm005',
        'RM006': 'rm006',
    }
    state = 'on' if is_active else 'off'
    ha_token = os.environ['HA_ACCESS_TOKEN']
    
    r = requests.post(
        f'http://ha-host:8123/api/states/input_boolean.room_occupied_{room_map[room_id]}',
        headers={'Authorization': f'Bearer {ha_token}', 'Content-Type': 'application/json'},
        json={'state': state}
    )
    # HA 自动化自动触发 CH5 ON/OFF
```

---

## 4. 独立自动化脚本（替代方案）

如果不希望使用 HA Packages，可以使用以下独立自动化配置：

### 4.1 单房间模板

```yaml
# automations/bt_power_template.yaml
# 适用于单个房间的蓝牙电源自动化模板
# 使用时替换 {{ ROOM_NAME }}、{{ ROOM_ID }}、{{ SLAVE_ID }}

- id: "bt_power_{{ ROOM_ID }}_on"
  alias: "蓝牙上电 - {{ ROOM_NAME }}（开单）"
  trigger:
    - platform: state
      entity_id: input_boolean.room_occupied_{{ ROOM_ID }}
      to: "on"
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.bt_power_{{ ROOM_ID }}
    - delay:
        seconds: 5
    - service: system_log.write
      data:
        message: "{{ ROOM_NAME }} 蓝牙模块已上电（CH5 ON）"
        level: info

- id: "bt_power_{{ ROOM_ID }}_off"
  alias: "蓝牙断电 - {{ ROOM_NAME }}（退单）"
  trigger:
    - platform: state
      entity_id: input_boolean.room_occupied_{{ ROOM_ID }}
      to: "off"
  action:
    - service: switch.turn_off
      target:
        entity_id: switch.bt_power_{{ ROOM_ID }}
    - service: system_log.write
      data:
        message: "{{ ROOM_NAME }} 蓝牙模块已断电（CH5 OFF）"
        level: info
```

### 4.2 用于 HA 蓝图 (Blueprint)

```yaml
blueprint:
  name: "蓝牙音频模块电源控制 — 继电器CH5"
  description: >
    当房间占用状态变化时，自动控制继电器CH5通断，
    实现蓝牙音频模块的随订单供电/断电。
  domain: automation
  input:
    room_name:
      name: 房间名称
      description: "例如：大会议室"
    room_id:
      name: 房间ID
      description: "例如：rm001"
    switch_entity:
      name: 蓝牙电源开关实体
      selector:
        entity:
          domain: switch

trigger:
  - platform: state
    entity_id: !input room_occupied
    id: "occupied_on"
    to: "on"
  - platform: state
    entity_id: !input room_occupied
    id: "occupied_off"
    to: "off"

action:
  - choose:
      - conditions:
          - condition: trigger
            id: "occupied_on"
        sequence:
          - service: switch.turn_on
            target:
              entity_id: !input switch_entity
          - delay:
              seconds: 5
          - service: system_log.write
            data:
              message: "{{ room_name }} 蓝牙模块已上电（CH5 ON）"
              level: info
      - conditions:
          - condition: trigger
            id: "occupied_off"
        sequence:
          - service: switch.turn_off
            target:
              entity_id: !input switch_entity
          - service: system_log.write
            data:
              message: "{{ room_name }} 蓝牙模块已断电（CH5 OFF）"
              level: info
```

---

## 5. 调试与验证

### 5.1 Modbus通讯测试

在HA开发者工具 → 服务中执行：

```yaml
service: switch.turn_on
target:
  entity_id: switch.bt_power_rm001
```

验证：
1. CH5继电器应发出"咔嗒"吸合声
2. 蓝牙模块LED指示灯亮起
3. 手机可搜索到 `高岸-大会议室` 蓝牙设备

```yaml
service: switch.turn_off
target:
  entity_id: switch.bt_power_rm001
```

验证：
1. CH5继电器释放
2. 蓝牙模块LED熄灭
3. 手机蓝牙列表中的 `高岸-大会议室` 设备信号消失

### 5.2 全流程验证

| 步骤 | 操作 | 预期结果 |
|------|------|---------|
| 1 | ERP开单（大会议室） | HA接收状态→CH5 ON→蓝牙模块上电 |
| 2 | 客人手机搜索蓝牙 | 30秒内搜到"高岸-大会议室" |
| 3 | 客人连接蓝牙播放音乐 | T-6715 LINE IN有音频输入→吸顶音箱出声 |
| 4 | ERP退单 | HA接收状态→CH5 OFF→蓝牙模块断电 |
| 5 | 蓝牙信号消失 | 手机蓝牙列表断开，"高岸-大会议室"不可见 |

---

## 6. 系统开发规约

### 6.1 蓝牙音频模块命名规范

| 字段 | 规约 |
|------|------|
| 蓝牙广播名 | `高岸-{房间名}`（如"高岸-大茶室C"） |
| 设备名称 | 使用房间中文全称，与ERP系统一致 |
| SSID隐藏 | 不隐藏，方便客人搜索发现 |

### 6.2 CH5通道保留规约

- **CH5 永久保留给蓝牙音频模块电源控制**，不得挪作他用
- 任何未来设计中新增的继电器负载分配方案不得占用 CH5
- CH5 对应 Modbus Holding Register 地址 `0x0005`

### 6.3 订单生命周期状态映射

| ERP 订单状态 | HA input_boolean | CH5 | 蓝牙模块 |
|-------------|-----------------|-----|---------|
| 空闲/无订单 | `off` | OFF | 断电熄灭 |
| 已预约（预开） | `on`（到店前15分钟） | ON | 通电启动 |
| 使用中 | `on` | ON | 正常工作 |
| 退单/结束 | `off` | OFF | 断电熄灭 |
| 保洁中 | `off` | OFF | 断电熄灭 |
| 维修中 | `off` | OFF | 断电熄灭 |

### 6.4 安全与防蹭连策略

1. **物理断电是最可靠的防蹭连手段**：CH5 OFF = 蓝牙模块彻底断电，任何外部设备都无法扫描或连接
2. **客人离店后无需手动断开蓝牙**：CH5 OFF 后手机自动断开连接，下次到店重新通电即可重新连接
3. **预开电时机**：建议在预约到店时间前15分钟预通电（CH5 ON），给蓝牙模块充分的启动时间
4. **异常处理**：如HA检测到CH5 ON但蓝牙模块未响应（无BLE广播），尝试重启CH5（先OFF再ON）

---

## 7. 关联文档

| 文档名称 | 文档编号 |
|---------|---------|
| 高岸ERP系统-盈隆店IoT接线实施指南（V1.2） | IOT-03 |
| 高岸ERP系统-IoT技术实施与家庭测试方案（V1.0） | IOT-02 |

---

## 8. 修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|-------|---------|
| V1.0 | 2026-05-17 | — | 初稿：基于方案B的CH5蓝牙电源控制完整配置 |
