# 高岸ERP系统-IoT集成测试指引

**文档编号**：TST-02
**版本**：V1.0
**日期**：2026年5月24日
**文档状态**：草稿
**关联文档**：IOT-02（IoT技术实施与家庭测试方案）、IOT-03（盈隆店IoT接线实施指南）、ARC-02（边缘控制层Spec）
**测试范围**：高岸ERP系统 IoT 集成模块后端 API（services/ha_service.py + routers/iot.py）

---

## 一、测试环境

| 项目 | 配置 |
|------|------|
| 后端服务 | FastAPI + Uvicorn，运行在 http://localhost:8000 |
| 数据模式 | **Mock 模式**（默认，无需 HA Token） |
| HA 模式 | 配置 `.env` 的 `HA_TOKEN` 后自动切换为真实 HA 模式 |
| 测试账户 | admin / admin123 |

### Mock 模式模拟数据

- **5 个房间**：大会议室 RM001、中茶室A RM002、中茶室B RM003、大茶室C RM004、展厅 RM005
- **30 台设备**：每房间 6 台（门锁×1、空调×1、主灯×1、辅灯×1、窗帘×1、音响×1）
- **7 个场景模板**：迎宾、品茶、会议、K歌、节能、退房、预开
- **N 条告警**：根据设备状态自动生成（离线告警、低电量告警）

---

## 二、前置条件

### 2.1 启动服务

```bash
cd server
pip install httpx        # 安装 HA 通信依赖（如未安装）
python run.py            # 启动服务，默认 http://localhost:8000
```

验证服务运行：

```bash
curl http://localhost:8000/api/health
# 预期: {"status":"ok","version":"V1.0","app":"高岸ERP API Server"}
```

### 2.2 配置切换（真实 HA 模式可选）

编辑 `server/.env`：

```ini
HA_URL=http://localhost:8123
HA_TOKEN=你的长期访问令牌
```

HA 令牌获取：HA Web UI → 右下角用户名 → 安全 → 长期访问令牌 → 创建。

配置后重启服务即可切换为真实 HA 模式。Mock 模式无需任何配置。

---

## 三、IoT 基础功能测试

### 3.1 HA 连接状态

```bash
curl http://localhost:8000/api/iot/health
```

预期响应（Mock 模式）：
```json
{"status":"ok","mode":"mock","device_count":30}
```

预期响应（真实 HA 模式）：
```json
{"status":"ok","mode":"ha"}
```

### 3.2 IoT 设备统计

```bash
curl http://localhost:8000/api/iot/stats
```

预期响应：
```json
{"total":30,"online":25,"offline":3,"fault":2,"online_rate":83.3,"unresolved_alerts":2,"total_alerts":5}
```

### 3.3 列出所有设备

```bash
curl http://localhost:8000/api/iot/devices
```

预期：返回 30 台设备的 JSON 数组，每台包含 device_id、room_id、type、name、ha_entity_id、protocol、slave_id、status、attributes。

### 3.4 按房间筛选设备

```bash
# 大会议室（RM001）应有 6 台设备
curl "http://localhost:8000/api/iot/devices?room_id=RM001"

# 中茶室A（RM002）应有 6 台设备
curl "http://localhost:8000/api/iot/devices?room_id=RM002"
```

### 3.5 按类型筛选设备

```bash
# 查看所有空调（共 5 台）
curl "http://localhost:8000/api/iot/devices?type=AC"

# 查看所有门锁（共 5 台）
curl "http://localhost:8000/api/iot/devices?type=Lock"

# 查看所有灯光（共 10 台）
curl "http://localhost:8000/api/iot/devices?type=Light"

# 查看所有窗帘（共 5 台）
curl "http://localhost:8000/api/iot/devices?type=Curtain"

# 查看所有音响（共 5 台）
curl "http://localhost:8000/api/iot/devices?type=Speaker"
```

### 3.6 查看单个设备

```bash
# 查看大会议室门锁
curl http://localhost:8000/api/iot/devices/DEV0001

# 查看大会议室空调
curl http://localhost:8000/api/iot/devices/DEV0002
```

### 3.7 设备参数验证

验证各设备的 Modbus 参数是否正确：

| 设备 | device_id | slave_id | sub_address | 协议 |
|------|-----------|----------|-------------|------|
| 大会议室门锁 | DEV0001 | — | — | Zigbee |
| 大会议室空调 | DEV0002 | 21 | — | Modbus |
| 大会议室主灯 | DEV0003 | 1 | 1 | Modbus |
| 大会议室辅灯 | DEV0004 | 1 | 2 | Modbus |
| 大会议室窗帘 | DEV0005 | 31 | — | Modbus |
| 大会议室音响 | DEV0006 | — | — | IPAudio |
| 中茶室A空调 | DEV0008 | 22 | — | Modbus |
| 中茶室B空调 | DEV0014 | 23 | — | Modbus |
| 大茶室C空调 | DEV0020 | 24 | — | Modbus |
| 展厅空调 | DEV0026 | 24 | — | Modbus |

```bash
# 验证：大会议室空调 slave_id = 21
curl http://localhost:8000/api/iot/devices/DEV0002 | python -c "import sys,json;d=json.load(sys.stdin);print(f'slave_id={d[\"slave_id\"]}')"
# 预期输出: slave_id=21
```

---

## 四、设备控制测试

### 4.1 登录获取 Token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

### 4.2 空调控制

```bash
# 设置大会议室空调温度为 22°C
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0002","action":"temperature","params":{"temperature":22}}'
```

预期响应中的 `new_state.target_temperature` 应为 22。

```bash
# 切换制冷模式
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0002","action":"cool"}'

# 关闭空调
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0002","action":"off"}'

# 切换制热模式
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0002","action":"heat"}'
```

### 4.3 灯光控制

```bash
# 开大会议室主灯（90% 亮度，5000K 色温）
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0003","action":"on","params":{"brightness":90,"color_temp":5000}}'

# 关大会议室主灯
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0003","action":"off"}'

# 调亮度
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0003","action":"brightness","params":{"brightness":50}}'
```

### 4.4 窗帘控制

```bash
# 打开窗帘
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0005","action":"open"}'

# 关闭窗帘
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0005","action":"close"}'
```

### 4.5 门锁控制

```bash
# 远程开门
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0001","action":"unlock"}'

# 上锁
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0001","action":"lock"}'
```

### 4.6 音响控制

```bash
# 播放背景音乐
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0006","action":"on","params":{"volume":30,"source":"背景音乐"}}'

# 调音量
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0006","action":"volume","params":{"volume":50}}'

# 暂停
curl -s -X POST http://localhost:8000/api/iot/control \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"DEV0006","action":"pause"}'
```

---

## 五、场景联动测试

### 5.1 场景列表

```bash
curl http://localhost:8000/api/iot/scenes
```

预期：返回 7 个场景，每个场景包含 scene_id、name、label、trigger_type、applicable_room_types、rules。

### 5.2 迎宾模式

在大会议室（RM001）激活迎宾模式。预期执行 5 个步骤：
1. 开门锁
2. 开灯（80% 亮度，3500K）
3. 开窗帘
4. 空调设置 24°C
5. 音响播放背景音乐

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM001","scene":"Welcome"}'
```

验证要点：
- `success` = true
- `total_steps` = 5
- `success_count` = 6（因为灯光有 2 台设备）
- 每个步骤的 `old_state` 和 `new_state` 正确反映状态变化

### 5.3 品茶模式

在中茶室A（RM002）激活品茶模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM002","scene":"TeaSession"}'
```

预期：暖光 60%/3000K、开窗帘、空调 25°C、播放古筝曲。

### 5.4 会议模式

在大会议室（RM001）激活会议模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM001","scene":"Meeting"}'
```

预期：冷白光 90%/5000K、开窗帘、空调 24°C。

### 5.5 K歌模式

在中茶室A（RM002）激活K歌模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM002","scene":"Karaoke"}'
```

预期：氛围光 30%/2500K、关窗帘、空调 22°C、音响 60% 音量。

### 5.6 节能模式

在大茶室C（RM004）激活节能模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM004","scene":"EnergySave"}'
```

预期：关灯、关窗帘、空调 26°C、关音响。

### 5.7 退房模式

在大茶室C（RM004）激活退房模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM004","scene":"Checkout"}'
```

预期：关空调、关灯、关窗帘、关音响、上锁。

### 5.8 预开模式

在大会议室（RM001）激活预开模式：

```bash
curl -s -X POST http://localhost:8000/api/iot/scenes/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"room_id":"RM001","scene":"PreOpen"}'
```

预期：空调预冷 24°C、播放轻音乐。

---

## 六、告警功能测试

### 6.1 查看告警列表

```bash
curl http://localhost:8000/api/iot/alerts
```

### 6.2 按级别筛选

```bash
# 严重告警
curl "http://localhost:8000/api/iot/alerts?severity=Error"

# 警告
curl "http://localhost:8000/api/iot/alerts?severity=Warning"

# 信息
curl "http://localhost:8000/api/iot/alerts?severity=Info"
```

### 6.3 按房间筛选

```bash
curl "http://localhost:8000/api/iot/alerts?room_id=RM001"
```

### 6.4 按状态筛选

```bash
# 未处理
curl "http://localhost:8000/api/iot/alerts?status=Unresolved"

# 已解决
curl "http://localhost:8000/api/iot/alerts?status=Resolved"
```

---

## 七、完整自动化测试

一键运行所有测试（覆盖 11 个测试点）：

```bash
cd server
python test_api.py
```

测试覆盖：
1. 健康检查
2. 认证测试（登录）
3. 商品分类
4. 商品管理
5. 门店与房间
6. 订单管理
7. 创建订单
8. 用户信息
9. **IoT 设备管理**（列表、筛选、统计、场景、告警）
10. **IoT 设备控制**
11. **IoT 场景激活**

---

## 八、验收标准

| 测试项 | 最低通过标准 | Mock 模式预期 | HA 模式预期 |
|--------|-------------|--------------|------------|
| IoT 健康检查 | status=ok | mode=mock | mode=ha |
| 设备列表 | ≥1 台设备 | 30 台 | 与 HA 配置一致 |
| 按房间筛选 | RM001=6 台 | 6 台 | 与 HA 配置一致 |
| 按类型筛选 | 类型数量匹配 | AC=5, Lock=5 | 与 HA 配置一致 |
| 设备控制 | success=true | 模拟状态变更 | 真实设备动作 |
| 场景激活 | success=true | 模拟场景执行 | 真实设备联动 |
| 场景步骤 | ≥3 步完成 | Welcome=5步 | 全部执行 |
| 告警列表 | ≥1 条 | 按设备状态生成 | HA 告警 |
| 统计 | total>0, online_rate 合理 | 30台/100% | 实时 HA 数据 |

---

## 九、切换到真实 HA 模式后的验证

配置 HA_TOKEN 后，额外验证以下项目：

### 9.1 HA 连通性

```bash
curl http://localhost:8000/api/iot/health
# 预期: {"status":"ok","mode":"ha"}
```

### 9.2 设备状态一致性

```bash
# Mock 模式与 HA 模式对比：同类型设备数量应一致
curl "http://localhost:8000/api/iot/devices?type=AC" | python -c "import sys,json;d=json.load(sys.stdin);print(f'AC devices: {len(d)}')"
```

### 9.3 真实设备控制

在 HA 模式下控制设备，应观察到：
- 空调：HA 中对应的 climate 实体状态变化
- 灯光：HA 中对应的 light 实体状态变化
- 窗帘：HA 中对应的 cover 实体实际动作
- 门锁：HA 中对应的 lock 实体实际动作

---

## 十、常见问题

### Q1: 服务无法启动

```bash
# 检查端口占用
netstat -ano | findstr :8000

# 检查依赖
pip list | findstr "fastapi uvicorn sqlalchemy aiosqlite httpx"
```

### Q2: 设备控制返回 401

未登录或 Token 过期。重新获取 Token：

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

### Q3: 设备控制返回 404

设备 ID 不存在，检查设备列表获取正确的 device_id。

### Q4: HA 连接失败

- 确认 HA 运行中：`curl http://localhost:8123`
- 确认 Token 有效：`curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8123/api/`
- 确认 `.env` 配置正确

---

## 附录：API 端点速查

| 端点 | 方法 | 是否需要认证 | 说明 |
|------|------|-------------|------|
| `/api/iot/health` | GET | 否 | HA 连接状态 |
| `/api/iot/devices` | GET | 否 | 设备列表（支持 room_id/type/status 筛选） |
| `/api/iot/devices/{id}` | GET | 否 | 单个设备详情 |
| `/api/iot/control` | POST | 是 | 设备控制 |
| `/api/iot/scenes` | GET | 否 | 场景列表 |
| `/api/iot/scenes/activate` | POST | 是 | 场景激活 |
| `/api/iot/alerts` | GET | 否 | 告警列表（支持 severity/status/room_id 筛选） |
| `/api/iot/stats` | GET | 否 | IoT 统计数据 |
| `/api/auth/login` | POST | 否 | 登录获取 Token |
