# 盈隆店 实体映射表

## 当前虚拟实体（input_boolean，WSL开发阶段）

| 区域 | 实体ID | 友好名称 | 当前状态 | 备注 |
|------|--------|----------|----------|------|
| 大茶室 | input_boolean.大茶室按键1 | 大茶室按键1 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室按键2 | 大茶室按键2 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室按键3 | 大茶室按键3 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室按键4 | 大茶室按键4 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室按键5 | 大茶室按键5 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室按键6 | 大茶室按键6 | off | 模拟面板 |
| 大茶室 | input_boolean.大茶室背景灯 | 大茶室背景灯 | off | 模拟开关 |
| 大茶室 | input_boolean.大茶室吊灯 | 大茶室吊灯 | off | 模拟开关 |
| 大会议室 | input_boolean.大会议室总开关 | 大会议室总开关 | off | 模拟开关 |
| 大会议室 | input_boolean.大会议室筒灯1 | 大会议室筒灯1 | off | 模拟开关 |
| 大会议室 | input_boolean.大会议室筒灯2 | 大会议室筒灯2 | off | 模拟开关 |
| 大会议室 | input_boolean.大会议室吊灯 | 大会议室吊灯 | off | 模拟开关 |
| 中茶室 | input_boolean.中茶室总开关 | 中茶室总开关 | off | 模拟开关 |
| 中茶室 | input_boolean.中茶室筒灯 | 中茶室筒灯 | off | 模拟开关 |
| 中茶室 | input_boolean.中茶室吊灯 | 中茶室吊灯 | off | 模拟开关 |
| 中茶室 | input_boolean.中茶室背景灯 | 中茶室背景灯 | off | 模拟开关 |
| 小茶室 | input_boolean.小茶室总开关 | 小茶室总开关 | off | 模拟开关 |
| 小茶室 | input_boolean.小茶室筒灯 | 小茶室筒灯 | off | 模拟开关 |
| 小茶室 | input_boolean.小茶室排风扇 | 小茶室排风扇 | off | 模拟开关 |

## 其他实体

| 实体ID | 类型 | 当前值 | 说明 |
|--------|------|--------|------|
| input_number.大茶室功放音量 | input_number | 50 | 功放音量百分比 |
| sensor.大茶室窗帘 | template | 已打开 | 窗帘状态模板 |
| sensor.大茶室功放状态 | template | 在线 | 功放在线状态 |

## 后续真实设备命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 灯光 | light.{区域}_{名称} | light.大茶室_吊灯 |
| 开关 | switch.{区域}_{名称} | switch.大茶室_背景灯 |
| 窗帘 | cover.{区域}_{名称} | cover.大茶室_窗帘 |
| 媒体 | media_player.{区域}_{名称} | media_player.大茶室_功放 |

## API端点速查

| 用途 | 方法 | URL |
|------|------|-----|
| 获取所有状态 | GET | /api/states |
| 调用服务 | POST | /api/services/{domain}/{service} |
| 获取配置 | GET | /api/config |
