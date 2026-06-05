# 高岸ERP系统-数据库设计

**文档编号**：DBA-01  
**版本**：V1.0  
**日期**：2026年6月2日  
**文档状态**：草稿  
**编制依据**：
- 《高岸ERP系统-对象模型设计》V1.2（ROM-01）
- 《高岸ERP系统-需求说明书》V10.12（REQ-01）
- SQLAlchemy 2.0 + SQLite（开发环境）/ PostgreSQL（生产环境）

---

## 一、设计概述

### 1.1 设计原则

1. **业务主键可见**：每个实体保留自增Integer `id` 作为物理主键，同时以 `String(32)` 业务主键（如 `storeId`, `orderId`）作为业务唯一标识和关联字段
2. **外键约束**：所有跨表关联使用业务主键作为 ForeignKey，确保数据完整性
3. **JSON 存储**：SQLite 环境下 JSON/Array 字段以 `Text` 类型存储，应用层负责序列化/反序列化
4. **命名规范**：表名使用 `snake_case` 复数形式；列名使用 `camelCase`；业务主键统一命名为 `XxxId`
5. **时间戳**：所有实体均包含 `createdAt` 列（`server_default=func.now()`）；部分实体含 `updatedAt` 列（`onupdate=func.now()`）

### 1.2 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| ORM | SQLAlchemy 2.0+ | 异步模式（DeclarativeBase） |
| 数据库（开发） | SQLite + aiosqlite | 零配置，单文件 |
| 数据库（生产） | PostgreSQL 16+ | 预留迁移方案 |
| 迁移 | SQLAlchemy create_all | 开发阶段自动建表；生产迁移使用 Alembic |

### 1.3 域划分

8个业务域（D01-D08），共114个实体：

| 域 | 编号 | 实体数 | 文件名 |
|----|------|--------|--------|
| 品牌运营 | D01 | 8 | `brand.py` |
| 门店拓展 | D02 | 15 | `store_dev.py` |
| 门店运营 | D03 | 13 | `operations.py` |
| 市场营销 | D04 | 10 | `marketing.py` |
| 供应链 | D05 | 17 | `supply_chain.py` |
| 财务 | D06 | 20 | `finance.py` |
| 人力资源 | D07 | 15 | `hr.py` |
| 技术 | D08 | 15 | `tech.py` |
| 遗留 | — | 1 | `user.py`（User 鉴权，过渡用） |

---

## 二、D01 品牌运营域（8张表）

### Organization — 组织
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| orgId | String(32) | PK, Unique | 组织编号 |
| parentOrgId | String(32) | FK→Organization.orgId | 上级组织（自引用） |
| name | String(100) | NOT NULL | 组织名称 |
| type | String(20) | NOT NULL | HQ / Franchisee |

### BusinessGoal — 经营目标
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| goalId | String(32) | PK, Unique | 目标编号 |
| orgId | String(32) | FK→Organization.orgId | 所属组织 |
| year | Integer | NOT NULL | 目标年份 |

### GoalMetric — 目标指标
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| metricId | String(32) | PK, Unique | 指标编号 |
| goalId | String(32) | FK→BusinessGoal.goalId | 所属目标 |
| metricName | String(50) | NOT NULL | 指标名称 |
| targetValue | Float | NOT NULL | 目标值 |
| actualValue | Float | — | 实际值 |

### BrandAsset — 品牌资产
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| assetId | String(32) | PK, Unique | 资产编号 |
| orgId | String(32) | FK→Organization.orgId | 所属组织 |
| assetType | String(30) | NOT NULL | Logo/VI/Manual/Template |
| version | String(20) | NOT NULL | 版本号 |

### Contract — 合同
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| contractId | String(32) | PK, Unique | 合同编号 |
| contractNumber | String(50) | Unique | 合同号 |
| orgId | String(32) | FK→Organization.orgId | 本方组织 |
| counterpartyId | String(32) | FK→Organization.orgId | 对方组织 |
| contractType | String(20) | NOT NULL | Franchise/Design/Management |

### Shareholder — 股东
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| shareholderId | String(32) | PK, Unique | 股东编号 |
| shareholderNumber | String(20) | Unique | 股东号 |
| type | String(20) | NOT NULL | Brand / Store |
| totalDividend | Float | default=0 | 累计分红 |

### Investment — 投资
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| investmentId | String(32) | PK, Unique | 投资编号 |
| shareholderId | String(32) | FK→Shareholder.shareholderId | 股东 |
| targetType | String(20) | NOT NULL | Brand / Store |
| shareRatio | Float | NOT NULL | 持股比例 |
| investmentAmount | Float | NOT NULL | 投资金额 |

### Milestone — 里程碑
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| milestoneId | String(32) | PK, Unique | 里程碑编号 |
| goalId | String(32) | FK→BusinessGoal.goalId | 关联目标 |

---

## 三、D02 门店拓展域（15张表）

### LegalEntity — 法律实体
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| legalEntityId | String(32) | PK, Unique | 实体编号 |
| creditCode | String(18) | Unique | 统一社会信用代码 |

### Territory — 行政区划
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| territoryId | String(32) | PK, Unique | 区划编号 |
| parentId | String(32) | FK→Territory.territoryId | 上级区划（自引用） |
| level | Integer | NOT NULL | 1=省 / 2=市 / 3=区 |

### Store — 门店
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| storeId | String(32) | PK, Unique | 门店编号 |
| storeCode | String(20) | Unique | 门店代码 |
| legalEntityId | String(32) | FK→LegalEntity.legalEntityId | 法律实体 |
| orgId | String(32) | FK→Organization.orgId | 运营组织 |
| territoryId | String(32) | FK→Territory.territoryId | 所在区划 |
| type | String(20) | NOT NULL | Direct / Franchise |
| status | String(20) | default=Operating | Operating/Suspended/Renovating/Closed |
| cleaningTimeout | Integer | default=30 | 保洁超时（分钟） |

### StoreSiteSelection — 选址
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| selectionId | String(32) | PK, Unique | 选址编号 |
| approvalStatus | String(20) | default=Pending | Pending/UnderReview/Approved/Rejected |

### StoreConstruction — 门店建设
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| constructionId | String(32) | PK, Unique | 建设编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| status | String(20) | default=Planned | Planned/InProgress/Completed/Sealed |

### ConstructionCost — 建设费用
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| costId | String(32) | PK, Unique | 费用编号 |
| constructionId | String(32) | FK→StoreConstruction.constructionId | 建设项目 |
| category | String(20) | NOT NULL | Decoration/Equipment/Material/Labor/Other |

### DesignDrawing — 设计图纸
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| drawingId | String(32) | PK, Unique | 图纸编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| type | String(20) | NOT NULL | Space/MEP/Fire/HVAC/Completion |
| fileFormat | String(10) | NOT NULL | DWG/PDF/PNG |

### Room — 房间
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| roomId | String(32) | PK, Unique | 房间编号 |
| roomCode | String(20) | NOT NULL | 房间代码（门店内唯一） |
| storeId | String(32) | FK→Store.storeId | 所属门店 |
| type | String(20) | NOT NULL | TeaRoom/MeetingRoom/Entertainment/Exhibition/Workspace |
| capacity | Integer | NOT NULL | 容纳人数 |

### RoomPricing — 房间定价
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| pricingId | String(32) | PK, Unique | 定价编号 |
| roomId | String(32) | FK→Room.roomId | 房间 |
| basePrice | Float | NOT NULL | 基础价格 |
| unit | String(20) | default=PerHour | PerHour / PerSession |

### RoomPersonPricing — 按人数定价
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| personPricingId | String(32) | PK, Unique | 定价编号 |
| roomId | String(32) | FK→Room.roomId | 房间 |
| personCount | Integer | NOT NULL | 人数 |
| pricePerHour | Float | NOT NULL | 每人每小时价格 |

### TimeSlotCoefficient — 时段系数
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| coeffId | String(32) | PK, Unique | 系数编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| dayType | String(20) | NOT NULL | Weekday/Weekend/Holiday |
| coefficient | Float | NOT NULL | 价格系数 |

### HolidayCalendar — 节假日日历
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| holidayId | String(32) | PK, Unique | 编号 |
| coefficient | Float | NOT NULL | 价格系数 |

### ActivityCalendar — 活动日历
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| activityId | String(32) | PK, Unique | 编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| coefficient | Float | NOT NULL | >1=溢价, <1=折扣 |

### DurationDiscountRule — 时长折扣
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| ruleId | String(32) | PK, Unique | 规则编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| minDuration | Integer | NOT NULL | 最少时长（分钟） |
| discountRate | Float | NOT NULL | 折扣率 |

### NightPackage — 夜间套餐
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| packageId | String(32) | PK, Unique | 套餐编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| packageType | String(20) | NOT NULL | Night / Overnight |

---

## 四、D03 门店运营域（13张表）

### Customer — 客户
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| customerId | String(32) | PK, Unique | 客户编号 |
| wxOpenId | String(100) | Unique | 微信OpenID |
| memberLevel | String(20) | default=Normal | Normal/Silver/Gold/Platinum |
| registerStoreId | String(32) | FK→Store.storeId | 注册门店 |

### CustomerTag — 客户标签
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| tagId | String(32) | PK, Unique | 标签编号 |
| customerId | String(32) | FK→Customer.customerId | 客户 |
| tagType | String(50) | NOT NULL | 标签类型 |
| tagValue | String(100) | NOT NULL | 标签值 |
| source | String(10) | Auto/Manual | 来源 |

### MemberCard — 会员卡
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| cardId | String(32) | PK, Unique | 卡编号 |
| cardNumber | String(20) | Unique | 卡号 |
| customerId | String(32) | FK→Customer.customerId | 客户 |

### RechargeRecord — 充值记录
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| rechargeId | String(32) | PK, Unique | 充值编号 |
| cardId | String(32) | FK→MemberCard.cardId | 会员卡 |
| paymentMethod | String(20) | NOT NULL | WxPay/AliPay/BankTransfer |

### Order — 订单
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| orderId | String(32) | PK, Unique | 订单编号 |
| orderNumber | String(30) | Unique | 订单号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| customerId | String(32) | FK→Customer.customerId | 客户 |
| roomId | String(32) | FK→Room.roomId | 房间（可空） |
| orderType | String(20) | NOT NULL | Room / Retail / Mixed |
| status | String(20) | default=PendingPay | 完整订单状态机 |
| platform | String(20) | NOT NULL | MiniProgram/MT/DY/Offline |

### OrderItem — 订单行
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| itemId | String(32) | PK, Unique | 行编号 |
| orderId | String(32) | FK→Order.orderId | 订单（级联删除） |
| itemType | String(20) | NOT NULL | Room / Product |

### RoomAppointment — 房间预约
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| appointmentId | String(32) | PK, Unique | 预约编号 |
| orderId | String(32) | FK→Order.orderId | 订单 |
| roomId | String(32) | FK→Room.roomId | 房间 |
| status | String(20) | default=Confirmed | Confirmed/InUse/Completed/Cancelled/NoShow |

### RoomStatus — 房间状态
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| statusId | String(32) | PK, Unique | 编号 |
| roomId | String(32) | FK→Room.roomId | 房间 |
| status | String(20) | NOT NULL | Free/Booked/InUse/Cleaning/Maintenance |

### CleaningTask — 保洁任务
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| taskId | String(32) | PK, Unique | 任务编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| roomId | String(32) | FK→Room.roomId | 房间 |
| assignedType | String(20) | NOT NULL | Employee / ExternalStaff |

### InspectionTemplate — 巡检模板
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| templateId | String(32) | PK, Unique | 模板编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |

### InspectionTask — 巡检任务
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| inspectionId | String(32) | PK, Unique | 任务编号 |
| storeId | String(32) | FK→Store.storeId | 门店 |
| templateId | String(32) | FK→InspectionTemplate.templateId | 模板 |

### InspectionItemResult — 巡检项结果
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| resultId | String(32) | PK, Unique | 结果编号 |
| inspectionId | String(32) | FK→InspectionTask.inspectionId | 任务 |
| category | String(20) | NOT NULL | Operation/Quality/Fire/Hygiene/Equipment |

### RectificationTask — 整改任务
| 列名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| rectificationId | String(32) | PK, Unique | 编号 |
| inspectionId | String(32) | FK→InspectionTask.inspectionId | 巡检任务 |
| itemResultId | String(32) | FK→InspectionItemResult.resultId | 巡检项 |

---

## 五、D04 市场营销域（10张表）

| 表名 | 说明 | 关键 FK |
|------|------|---------|
| campaigns | 营销活动 | storeId→Store.storeId |
| coupon_templates | 优惠券模板 | — |
| coupons | 优惠券实例 | templateId→CouponTemplate, customerId→Customer, orderId→Order |
| leads | 销售线索 | customerId→Customer, storeId→Store |
| opportunities | 商机 | leadId→Lead, customerId→Customer, storeId→Store |
| marketing_lists | 营销名单 | storeId→Store |
| customer_segments | 客户分群 | — |
| third_party_activities | 第三方活动 | storeId→Store |
| campaign_effects | 活动效果 | campaignId→Campaign |
| channels | 渠道 | — |

---

## 六、D05 供应链域（17张表）

| 表名 | 说明 | 关键 FK |
|------|------|---------|
| product_categories | 商品分类 | storeId→Store, parentId→自引用 |
| products | 商品 | categoryId→ProductCategory, storeId→Store |
| product_images | 商品图片 | productId→Product（级联删除） |
| units_of_measure | 计量单位 | — |
| price_lists | 价格表 | — |
| suppliers | 供应商 | — |
| supplier_prices | 供应商报价 | supplierId→Supplier, productId→Product |
| purchase_orders | 采购订单 | storeId→Store, supplierId→Supplier |
| purchase_order_lines | 采购订单行 | purchaseOrderId→PurchaseOrder（级联删除）, productId→Product |
| transfer_requests | 调拨申请 | fromStoreId→Store, toStoreId→Store |
| internal_settlements | 内部结算 | transferRequestId→TransferRequest, fromStoreId/toStoreId→Store |
| warehouses | 仓库 | storeId→Store |
| inventory_lots | 库存批次 | warehouseId→Warehouse, productId→Product |
| inventory_on_hand | 现有库存 | warehouseId→Warehouse, productId→Product |
| inventory_transfers | 库存转移 | fromWarehouseId/toWarehouseId→Warehouse, productId→Product |
| stock_counts | 盘点单 | warehouseId→Warehouse, storeId→Store |
| stock_count_lines | 盘点单行 | countId→StockCount（级联删除）, productId→Product |

---

## 七、D06 财务域（20张表）

| 表名 | 说明 | 关键 FK |
|------|------|---------|
| account_subjects | 会计科目 | parentId→自引用 |
| fiscal_calendars | 财务日历 | — |
| journal_entries | 凭证 | periodId→FiscalCalendar |
| journal_entry_lines | 凭证行 | entryId→JournalEntry（级联删除）, subjectId→AccountSubject |
| ledgers | 分类账 | subjectId→AccountSubject, periodId→FiscalCalendar |
| budgets | 预算 | orgId→Organization, storeId→Store |
| revenue_flows | 收入流水 | storeId→Store, orderId→Order |
| expense_records | 费用记录 | storeId→Store |
| advance_requests | 预支申请 | storeId→Store |
| reimbursements | 报销 | storeId→Store |
| payments | 付款 | storeId→Store |
| accounts_payable | 应付账款 | supplierId→Supplier, storeId→Store, purchaseOrderId→PurchaseOrder |
| reconciliation_tickets | 对账单 | storeId→Store |
| daily_settlements | 日结 | storeId→Store |
| monthly_settlements | 月结 | storeId→Store |
| dividend_records | 分红记录 | monthlySettlementId→MonthlySettlement, shareholderId→Shareholder, storeId→Store |
| fixed_assets | 固定资产 | storeId→Store |
| depreciation_records | 折旧记录 | assetId→FixedAsset |
| bank_accounts | 银行账户 | legalEntityId→LegalEntity |
| invoices | 发票 | storeId→Store |

---

## 八、D07 人力资源域（15张表）

| 表名 | 说明 | 关键 FK |
|------|------|---------|
| departments | 部门 | storeId→Store, parentId→自引用 |
| positions | 岗位 | departmentId→Department |
| jobs | 职务 | — |
| salary_grades | 薪级 | — |
| promotion_records | 晋升记录 | fromPositionId/toPositionId→Position, fromSalaryGradeId/toSalaryGradeId→SalaryGrade |
| employees | 员工 | storeId→Store, departmentId→Department, positionId→Position, jobId→Job, salaryGradeId→SalaryGrade |
| external_staff | 外部人员 | storeId→Store |
| schedules | 排班 | storeId→Store, employeeId→Employee |
| schedule_swaps | 换班 | fromEmployeeId/toEmployeeId→Employee, scheduleId→Schedule |
| attendances | 考勤 | storeId→Store, employeeId→Employee |
| leave_requests | 请假 | employeeId→Employee |
| payrolls | 工资单 | storeId→Store, employeeId→Employee |
| payroll_items | 工资单项 | payrollId→Payroll（级联删除） |
| performance_reviews | 绩效考核 | employeeId→Employee, storeId→Store |
| cleaner_assessments | 保洁考评 | storeId→Store, staffId→ExternalStaff |

---

## 九、D08 技术域（15张表）

| 表名 | 说明 | 关键 FK |
|------|------|---------|
| iot_devices | IoT设备 | roomId→Room |
| device_events | 设备事件 | deviceId→IoTDevice |
| smart_scenes | 智能场景 | — |
| scene_rules | 场景规则 | sceneId→SmartScene（级联删除） |
| room_scene_bindings | 房间场景绑定 | roomId→Room, sceneId→SmartScene |
| user_accounts | 系统用户账号 | orgId→Organization |
| roles | 角色 | orgId→Organization |
| permissions | 权限 | roleId→Role |
| audit_logs | 审计日志 | — |
| alert_rules | 告警规则 | — |
| alert_records | 告警记录 | ruleId→AlertRule, deviceId→IoTDevice |
| system_jobs | 系统任务 | — |
| backup_records | 备份记录 | — |
| command_queues | 命令队列 | deviceId→IoTDevice |
| heartbeat_records | 心跳记录 | deviceId→IoTDevice |

---

## 十、核心状态机

### Order 状态机
```
PendingPay → PendingUse → InUse → Completed
       ↘ Cancelled              ↘ Refunded
```
- PendingPay → Cancelled（未支付取消）
- PendingUse → Cancelled（未使用取消）
- Completed → Refunded（售后退款）

### CleaningTask 状态机
```
Pending → Accepted → InProgress → Completed
```

### InspectionTask 状态机
```
Pending → InProgress → Submitted → Reviewed
```

### DailySettlement 状态机
```
Open → Closed → Reviewed
```

---

## 十一、关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 物理主键 | Integer auto-increment | SQLite 性能优化，避免 String PK 的存储开销 |
| 业务主键 | String(32) UUID | 分布式环境唯一性，业务可读 |
| 表命名 | snake_case 复数 | SQL 标准约定 |
| 列命名 | camelCase | Python 对象属性风格，避免下划线过多 |
| JSON 存储 | Text + 应用层序列化 | SQLite 原生不支持 JSON 列（3.38+ 支持但为保证兼容） |
| 级联删除 | ORM 层 cascade | 与数据库层 FOREIGN KEY ON DELETE CASCADE 配合 |
| 跨域引用 | 业务主键 FK | 域间解耦，避免 Integer ID 歧义 |

---

## 十二、实体关系总览

```
D01 品牌运营 ◄────┐
                   │
D02 门店拓展 ── Store ──────────────────────┐
                   │                         │
D03 门店运营 ── Customer ── Order ───────────┤
                   │                         │
D04 市场营销 ── Campaign ── Coupon ────────┤
                   │                         │
D05 供应链   ── Product ── PurchaseOrder ──┤
                   │                         │
D06 财务     ── RevenueFlow ── Payment ────┤
                   │                         │
D07 人力资源 ── Employee ── Schedule ──────┤
                   │                         │
D08 技术     ── IoTDevice ── SmartScene ───┘
```

Store（门店）是全域核心枢纽，贯穿 D01-D08 所有业务域。

---

## 十三、迁移与部署

### 开发环境
```bash
# 自动建表（已测试通过）
python -c "import asyncio; from database import init_db, close_db; asyncio.run(init_db()); asyncio.run(close_db())"
```

### 生产环境迁移策略
1. 开发阶段：`Base.metadata.create_all` 自动建表
2. 生产上线：使用 Alembic 生成迁移脚本，逐版本管理 schema 变更
3. 数据迁移：编写数据迁移脚本，从旧表（`room_orders`, `shop_orders` 等）导入到新表

### 现有旧表兼容
| 旧表（待废弃） | 新表 | 迁移状态 |
|---------------|------|---------|
| `room_orders` | `orders` + `room_appointments` | 待迁移 |
| `shop_orders` / `shop_order_items` | `orders` + `order_items` | 待迁移 |
| `iot_alerts` | `alert_records` | 待迁移 |
| `iot_scenes` | `smart_scenes` | 已兼容 |

---

## 附录：索引策略

- 所有业务主键（XxxId）自动建立唯一索引
- 所有 ForeignKey 列建立非唯一索引
- 常用查询列：`status`、`storeId`、`customerId`、`roomId`、`date` 类列根据查询模式补充索引

---

> **文档关联**：ROM-01（对象模型原始定义）→ DBA-01（数据库物理实现）→ API-01（接口设计，待启动）
