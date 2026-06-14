# ERP ↔ HA IoT 接口规范
版本: v1.1
最后更新: 2026-06-14

## 一、架构概览

```
战66（前台ERP） ←→ M710Q（HA主机，放茶室）
  同局域网          │
                    ├── USB-485 → 485总线 → 开关面板/温控器/继电器
                    ├── 小米多模网关2 → 窗帘电机（米家WiFi版）
                    └── 通通锁G2 → 门锁
```

- **M710Q** 直接放茶室，USB-485直插，HA原生Modbus RTU串口控制
- **战66 ERP** 同局域网通过 HA REST API 控制设备
- 不需要485桥接器，不需要Tailscale

## 二、通信方式

ERP通过 **HA REST API** 控制IoT设备。
HA地址: `http://192.168.2.65:8123`（M710Q固定IP）
认证: Bearer Token（有效期长，需定期刷新）

## 三、房间命名对照

| 房间原名 | HA系统ID |
|:--------:|:--------:|
| 会议室（丰沙里） | fengshali |
| 小茶室（翡冷翠） | feilengcui |
| 中茶室（布拉格） | bulage |
| 大茶室（白沙瓦） | baishawa |

## 四、API接口

### 0. 获取HA API Token
```
HA界面 → 用户头像 → 安全 → 长期访问令牌 → 创建
```
返回一个JWT字符串，ERP启动时配置。

### 1. 获取所有设备状态
```
GET /api/states
```
返回所有实体的当前状态（开关、温度、模式等）。

### 2. 获取单个实体状态
```
GET /api/states/switch.baishawa_relay_ch1
```

### 3. 开关灯
```
POST /api/services/switch/turn_on
Body: {"entity_id": "switch.baishawa_relay_ch1"}

POST /api/services/switch/turn_off
Body: {"entity_id": "switch.baishawa_relay_ch1"}
```

### 4. 一键全屋开关
```
POST /api/services/switch/turn_on
Body: {"entity_id": "switch.baishawa_all_lights"}

POST /api/services/switch/turn_off
Body: {"entity_id": "switch.baishawa_all_lights"}
```

### 5. 空调控制
```
# 开空调
POST /api/services/climate/turn_on
Body: {"entity_id": "climate.baishawa"}

# 关空调
POST /api/services/climate/turn_off
Body: {"entity_id": "climate.baishawa"}

# 调温度
POST /api/services/climate/set_temperature
Body: {
  "entity_id": "climate.baishawa",
  "temperature": 25
}

# 切换模式（制冷/制热/送风）
POST /api/services/climate/set_hvac_mode
Body: {
  "entity_id": "climate.baishawa",
  "hvac_mode": "cool"
}
```
hvac_mode 可选值: cool（制冷）, heat（制热）, fan_only（送风）, off（关闭）

### 6. 查询室温
```
GET /api/states/sensor.baishawa_temp
```
返回: {"state": "25.5", "attributes": {"unit_of_measurement": "°C"}}

### 7. 窗帘控制
```
# 打开
POST /api/services/cover/open_cover
Body: {"entity_id": "cover.baishawa_curtain"}

# 关闭
POST /api/services/cover/close_cover
Body: {"entity_id": "cover.baishawa_curtain"}

# 停
POST /api/services/cover/stop_cover
Body: {"entity_id": "cover.baishawa_curtain"}

# 开到指定位置
POST /api/services/cover/set_cover_position
Body: {"entity_id": "cover.baishawa_curtain", "position": 50}
```

### 8. 门锁控制（通通锁）
```
# 远程开锁
POST /api/services/lock/unlock
Body: {"entity_id": "lock.baishawa_door"}

# 查门锁状态
GET /api/states/lock.baishawa_door
```

### 9. 场景切换
```
# 会客模式
POST /api/services/input_boolean/turn_on
Body: {"entity_id": "input_boolean.baishawa_scene_welcome"}

# 全关（初始化复位）
POST /api/services/input_boolean/turn_on
Body: {"entity_id": "input_boolean.baishawa_init"}
```

## 五、实体命名规则

```
switch.{房间}_relay_ch{1-8}     → 灯光继电器通道
switch.{房间}_all_lights         → 一键全开/全关
climate.{房间}                   → 空调温控器
cover.{房间}_curtain              → 窗帘
lock.{房间}_door                  → 通通锁门锁
sensor.{房间}_temp                → 室温
sensor.{房间}_humidity            → 湿度
input_boolean.{房间}_scene_xxx    → 场景切换
input_boolean.{房间}_init          → 初始化复位
```

房间名: baishawa, bulage, feilengcui, fengshali

## 六、Claude Code开发要点

### 需要实现的ERP功能

1. **房间状态面板**
   - 显示每个房间的灯状态（开/关）、温度、空调状态
   - 实时更新（前端轮询或监听）

2. **灯光控制**
   - 每个房间展示各路灯光开关按钮
   - 一键全开/全关

3. **空调控制**
   - 温度调节（加减/滑块）
   - 开关空调
   - 模式切换（制冷/制热/送风）

4. **窗帘控制**
   - 打开/关闭/停止
   - 显示开合百分比

5. **场景控制**
   - 会客模式（开灯、调温、开帘）
   - 离开模式（关灯、关空调、关帘、关门）

6. **门锁**
   - 远程开锁按钮
   - 门锁状态显示

### 接口调用示例（Python）

```python
import requests

HA_URL = "http://192.168.2.65:8123"
TOKEN = "你的HA长期访问令牌"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 开灯
requests.post(f"{HA_URL}/api/services/switch/turn_on",
    json={"entity_id": "switch.baishawa_relay_ch1"},
    headers=headers)

# 调温
requests.post(f"{HA_URL}/api/services/climate/set_temperature",
    json={"entity_id": "climate.baishawa", "temperature": 25},
    headers=headers)

# 查状态
resp = requests.get(f"{HA_URL}/api/states", headers=headers)
print(resp.json())
```

### 错误处理

- HA不可达（网络问题）→ 显示"设备离线"提示
- 返回HTTP 401 → Token过期，提示联系管理员刷新
- 返回HTTP 404 → entity_id不存在，记录日志

## 七、部署注意事项

- HA侧所有实体已在 configuration.yaml 中定义
- M710Q到茶室后，HA通过USB-485直连总线（Modbus RTU串口）
- 如在开发期测试，可先用Modbus模拟器
- 继电器通道编号（ch1-ch8）与每个房间的实际485设备对应，等茶室现场配码确认后不可随意更改
