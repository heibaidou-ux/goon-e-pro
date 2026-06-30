# 高岸ERP系统-开发日志 V1.9

> **时间范围**：2026年6月6日 — 2026年7月1日  
> **当前版本**：1.9.49（小程序） / V1.1（后端API）  
> **状态**：已上线生产  

---

## 一、总体进展

本期完成ERP系统从开发到上线的全部冲刺工作，目前系统已在盈隆店正式运行。

### 上线功能概览

| 模块 | 状态 | 说明 |
|------|------|------|
| 客人端小程序 | ✅ 已上线 | 首页/房间浏览/预订/茶品购买/支付/会员中心/房间智控 |
| 店员端小程序 | ✅ 已上线 | 工作台/房态/设备控制/保洁/考勤/排班/对账/巡检 |
| 后台管理(admin-web) | ✅ 已构建 | Vue3+TDesign，28页面覆盖供应链/财务/HR/营销/IoT |
| IoT设备控制 | ✅ HA已打通 | 81个真实HA实体在线，灯光/空调/窗帘/风扇/门锁可控 |
| 微信支付 | ✅ 已配置 | 统一下单+回调通知+IoT支付联动 |
| 场景联动 | ✅ 已配置 | 迎宾/品茶/会议/K歌/节能/退房/预开7种场景 |

---

## 二、版本迭代记录

### V1.9.0 — 三端合一账号体系（6月8日-6月10日）

- 客人端/店员端/后台管理三端统一用户表
- 角色路由：guest→客人端，staff→店员端，shareholder→股东工作台
- 微信一键登录 + 手机验证码登录 + 密码登录
- 员工独立登录入口

### V1.9.1-1.9.3 — 首页/预订/订单 MVP完善（6月10日-6月16日）

- 首页布局对齐交互原型：轮播图/快捷入口/包间卡片/茶品列表
- 日期选择栏横向滚动5天+更多按钮
- 自定义bottom-nav组件，替换所有内联导航
- 订单管理：进行中/待使用/已完成Tab切换
- 茶品区域：消除边距+数量增减(+/-)+详情弹窗+购物车

### V1.9.4-1.9.10 — 品牌色统一+评审修改（6月16日-6月19日）

- 全页面品牌色统一：#5D8A6B 茶绿
- 圆角16px统一，白底阴影卡片
- 六期评审修改覆盖40+项目
- 三端品牌色对齐（去旧蓝色#0052D9）

### V1.9.11-1.9.20 — 店员端完善+考勤/排班/保洁（6月19日-6月23日）

- 考勤完整事件链（多次签到签退）
- 保洁接单/完成流程
- 排班管理
- 巡检记录+复核
- 设备监控面板
- 对账页面

### V1.9.21-1.9.30 — IoT集成+485直连（6月23日-6月28日）

- Home Assistant REST API集成
- 485继电器直连网关
- MQTT桥接
- 场景联动引擎（Welcome/Checkout/TeaSession等）
- 微信支付回调→IoT联动（支付成功自动预开模式）
- 订单到期自动结束+跨日显示
- 实体发现/校准API

### V1.9.31-1.9.49 — 上线冲刺（6月29日-7月1日）

#### 6月29日
- 茶品扩充到12种+数据库seed同步更新
- VPS一键部署脚本
- 10项修复合集：预开空调提前5分钟/签到开门联动/客服通电API/背景色紫改浅绿/窗帘各3台/开门弹窗确认/店员真实名显示/付款去支付宝
- 房间控制页深黑改浅绿背景
- 登录页去默认账号+room-control去硬编码改用API动态

#### 6月30日
- **ha_service.py重大修复**：删除662行重复代码（文件被粘贴了两套），修复灯光关了又开Bug
- 继电器通道按描述词自动判断类型（换气扇/风扇/功放不再误标为Light）
- 补齐Speaker/BGM/Fan/ExhaustFan的HA实体映射
- 去掉所有页面支付宝选项
- 微信支付图标统一为官方logo
- 微信支付openid自动获取（从wechat_openid / wx.login code）
- 密码错误401→400，防止前端拦截跳转客人页
- 客人端隐藏全屋灯光总开关→恢复全屋灯光
- 所有controlDevice加具体错误提示，静默catch改为报错+回滚
- 登录页改版：默认显示微信登录，手机号验证码登录藏为二级入口

#### 7月1日
- 房间列表/设备清单全部动态化（去硬编码RM001-004）
- 设备清单按房间类型（TeaRoom/MeetingRoom）自动生成
- HA_ENTITY_ROOM_MAP精简为4行标准前缀（bai_sha_wa/bu_la_ge/fei_leng_cui/feng_sha_li）
- 弹窗留白修复（开门菜单/房间选择器）
- product.py marketPrice支持NULL值（防500）
- 测试产品/房间创建脚本

---

## 三、IoT设备控制链路

```
客人端小程序 → wx.requestPayment → 后端API
                                       ↓
后端API → FastAPI → controlDevice() → Home Assistant REST API
                                       ↓
Home Assistant → 485继电器网关 → 物理设备（灯光/风扇/空调）
               → Zigbee门锁（通通锁）
               → RS485窗帘电机
               → 音响（背景音乐）
```

### HA实体命名规范（v1.1）

| 实体类型 | 命名规则 | 示例 |
|---------|---------|------|
| 继电器灯光 | switch.{房间}_relay_ch{N} | switch.baishawa_relay_ch1 |
| 全屋灯光 | switch.{房间}_all_lights | switch.baishawa_all_lights |
| 空调 | climate.{房间} | climate.baishawa |
| 窗帘 | cover.{房间}_curtain | cover.baishawa_curtain |
| 门锁 | lock.{房间}_door | lock.baishawa_door |
| 室温 | sensor.{房间}_temp | sensor.baishawa_temp |
| 湿度 | sensor.{房间}_humidity | sensor.baishawa_humidity |
| 场景切换 | input_boolean.{房间}_scene_{场景} | input_boolean.baishawa_scene_welcome |

### 房间名对照

| ERP房间ID | ERP名称 | HA系统名 | 实际位置 |
|-----------|---------|----------|---------|
| RM004 | 白沙瓦 | baishawa | 大茶室 |
| RM002 | 布拉格 | bulage | 中茶室 |
| RM003 | 翡冷翠 | feilengcui | 小茶室 |
| RM001 | 丰沙里 | fengshali | 会议室 |

---

## 四、数据库结构

### 表清单（20+表）

| 域 | 表 | 说明 |
|----|---|------|
| 用户 | users | 统一用户表（guest/staff/shareholder） |
| 门店 | stores | 门店信息（盈隆店/花城广场店） |
| 房间 | rooms / room_pricings | 房间配置+定价 |
| 商品 | products / product_categories | 茶品/茶具/套餐 |
| 订单 | orders / shop_orders | 房间订单+茶品订单 |
| IoT | iot_devices / alert_records / smart_scenes | 设备/告警/场景 |
| HR | employees / attendance_records / schedule_entries | 员工/考勤/排班 |
| 财务 | revenue_flows / expense_records / settlement | 收入/支出/月结 |
| 供应链 | suppliers / purchase_orders / inventory | 供应商/采购/库存 |

---

## 五、环境配置

| 环境 | 地址 | 说明 |
|------|------|------|
| 生产VPS | https://erp.highbank.cn | 阿里云，Docker部署 |
| 小程序appid | wx181568857908b5ae | 高岸荟（客人端）/ 高岸ERP店员端 |
| 微信商户号 | 1747166566 | 微信支付已配置 |
| Home Assistant | http://192.168.2.65:8123 | 茶室本地小主机 |
| 485网关 | 127.0.0.1:7003 | FRP隧道穿透 |
| 数据库 | SQLite (gaoan_erp.db) | 生产环境建议迁PostgreSQL |

---

## 六、已知问题/待办

1. **微信支付**：商户平台需添加本机IP到白名单，否则CI上传会报IP限制
2. **商品数据**：当前DB中只有4条演示商品，需上线后替换为真实茶室商品清单
3. **HA设备完全覆盖**：81个实体已在线，仍需逐房间逐个设备验证控制指令
4. **admin-web部署**：已构建但尚未部署到VPS（前端dist包需要上传）
5. **短信验证码**：目前硬编码为8888，需接入阿里云/腾讯云短信服务
6. **数据库升级**：SQLite适合初期，业务增长后建议迁PostgreSQL
