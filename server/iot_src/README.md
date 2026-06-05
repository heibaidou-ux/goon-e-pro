# 盈隆店 HA IoT 边缘控制系统

## 架构
ERP（店员端） → HA (M710Q) → 物理设备（聚英继电器/485总线）

## 目录结构
```
yinglong-iot/
├── scripts/              # 控制脚本
│   ├── control_light.py  # 灯光控制
│   ├── query_states.py   # 状态查询
│   └── simulate_panel.py # 模拟面板
├── automations/          # HA自动化场景
├── mqtt_bridge/          # MQTT桥接
└── docs/                 # 文档
```

## 快速开始
```bash
pip install -r requirements.txt
cp .env.example .env   # 编辑HA地址和Token
python scripts/query_states.py  # 测试连接
```

## 开发原则
1. 先模拟再联调 — 所有代码在WSL上用虚拟input_boolean跑通
2. 每个功能一个脚本 — 单一职责
3. 配置文件与代码分离

## 部署目标
- HA地址：http://192.168.2.65:8123 （M710Q Docker）
- 开发环境：战66 WSL
