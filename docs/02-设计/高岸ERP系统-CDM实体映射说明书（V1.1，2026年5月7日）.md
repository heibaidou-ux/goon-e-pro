# 高岸ERP系统-CDM实体映射说明书

> 本文档为 高岸ERP系统-需求说明书 的附属文档，提供各业务域与 Microsoft Common Data Model（CDM）的详细逐域实体映射。

**版本**：V1.1  
**日期**：2026年5月7日  
**关联文档**：REQ-01（高岸ERP系统-需求说明书）第2.5节  
**维护规则**：随对象模型设计更新同步修订

---

## 1. 映射说明

### 1.1 CDM简介

Microsoft Common Data Model（CDM）是微软维护的开源标准业务数据模型，包含 5,000+ 预定义业务实体，按以下逻辑分组组织：

| CDM分组 | 说明 | 适用场景 |
|---------|------|---------|
| applicationCommon | 应用层通用实体 | 客户、营销、服务、用户等跨行业通用概念 |
| foundationCommon | 基础业务实体 | 订单、商品、发票、价格等交易基础 |
| operationsCommon | 运营管理实体 | 财务、供应链、人力资源等运营管理 |
| industryCommon | 行业专用实体 | 各垂直行业特有概念 |

### 1.2 映射类型定义

| 映射类型 | 说明 |
|---------|------|
| **精确映射** | 高岸ERP概念与CDM实体高度吻合，可直接复用CDM实体定义及属性 |
| **近似映射** | 高岸ERP概念与CDM实体基本匹配，需通过扩展属性（Extension）适配部分高岸特有需求 |
| **概念映射** | CDM无直接对应实体，需参考CDM的设计模式自定义实体，或通过组合已有实体实现 |

### 1.3 统计总览

| 业务域 | 实体数量 | 精确映射 | 近似映射 | 概念映射 |
|-------|---------|---------|---------|---------|
| D01 品牌运营域 | 7 | 0 | 5 | 2 |
| D02 门店拓展域 | 3 | 0 | 2 | 1 |
| D03 门店运营域 | 12 | 8 | 2 | 2 |
| D04 市场营销域 | 9 | 5 | 1 | 3 |
| D05 供应链域 | 15 | 12 | 1 | 2 |
| D06 财务域 | 14 | 10 | 3 | 1 |
| D07 人力资源域 | 10 | 7 | 1 | 2 |
| D08 技术域 | 5 | 2 | 1 | 2 |
| **合计** | **75** | **44** | **16** | **15** |

---

## 2. 逐域实体映射

### 2.1 D01 品牌运营域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 组织/品牌 | Organization | applicationCommon | 近似映射 | CDM Organization 作为品牌主体，管理品牌基本信息、注册信息、品牌分级 |
| 经营目标 | Goal | applicationCommon | 近似映射 | 映射年度/季度/月度经营目标，含营收目标、利润目标、门店数量目标，支持目标分解与跟踪 |
| 目标指标 | GoalMetric | applicationCommon | 近似映射 | 与 Goal 配合，定义具体的量化指标（目标值、实际值、完成率） |
| 品牌资产 | — | — | 概念映射 | CDM 无直接品牌资产实体；品牌标准、VI 规范、物料模板等通过 Document/Note 实体关联 Organization |
| 加盟合同 | Contract | applicationCommon | 近似映射 | CDM Contract 作为与加盟商的签约合同实体，管理合同版本、期限、续约 |
| 投资者关系 | — | — | 概念映射 | 高岸特有的投资者视图需求；投资者可映射为 Account（类型=投资者），投资关系通过自定义 Investment 实体关联门店 BusinessUnit |
| 看板/仪表盘 | Goal + GoalMetric | applicationCommon | 近似映射 | 品牌运营看板和投资者看板的数据源来自 Goal（目标）和 GoalMetric（指标执行值）的聚合 |

### 2.2 D02 门店拓展域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 门店 | BusinessUnit | applicationCommon | 近似映射 | 每个门店映射为一个 BusinessUnit，按门店维度进行独立核算；门店类型（直营/加盟）、门店参数（面积/包间数/设施配置）存于扩展字段 |
| 销售区域 | Territory | applicationCommon | 近似映射 | 门店所在区域的划分（如福田区、南山区），用于区域分析和加盟区域授权 |
| 设计图/施工图 | Document | applicationCommon | 概念映射 | CDM Document 实体管理门店设计图、施工图、水电图、竣工图等文档；关联 BusinessUnit 实现图纸归档与版本管理 |

### 2.3 D03 门店运营域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 客人/客户 | Account | applicationCommon | 精确映射 | CDM Account 作为"客户"主体，存储客人的姓名、联系方式、会员等级、注册时间等，是高岸客户数据的核心实体 |
| 客人联系人 | Contact | applicationCommon | 精确映射 | 存储客人附加联系人信息（企业客户对接人、紧急联系人等），与 Account 多对一关联 |
| 预约单/零售订单 | Order | foundationCommon | 精确映射 | CDM Order 标准销售订单，高岸中预约即生成 Order，状态跟踪预约→到店→完成；零售订单复用同一实体 |
| 订单明细（包间/商品） | OrderProduct | foundationCommon | 精确映射 | Order 的行项目，映射包间租赁时段、零售商品明细，含数量、单价、金额 |
| 包间/会议室 | Service | applicationCommon | 近似映射 | CDM Service 表示可预订服务，高岸包间作为可预订资源映射至此；设施属性（容量、价格）存于扩展字段 |
| 预约行为 | Appointment | applicationCommon | 精确映射 | 映射客人的预约行为，含时间范围、参与人、备注，与 Order 和 Service 关联 |
| 商品 | Product | foundationCommon | 精确映射 | 映射茶叶、茶具、茶点等零售商品，含分类、价格、规格、库存单位 |
| 保洁任务 | Task | applicationCommon | 精确映射 | CDM Task 通用任务实体，映射保洁任务，含指派对象、状态、截止时间、完成确认 |
| 巡检记录 | Inspection | — | 概念映射 | CDM 无直接对应；概念上映射至 applicationCommon Activity 扩展，或自定义 Inspection 实体 |
| 房态（包间状态） | — | — | 概念映射 | 高岸特有概念，通过 Service 实体的状态字段 + 扩展属性实现 |
| 消费流水 | Order | foundationCommon | 精确映射 | 消费流水复用 Order 实体，通过订单类型标签区分不同业务线 |
| 退款/取消记录 | Order | foundationCommon | 近似映射 | 通过 Order 状态字段（Cancelled/Refunded）追溯，退款明细存于扩展 OrderProduct |

### 2.4 D04 市场营销域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 营销活动 | Campaign | applicationCommon | 精确映射 | CDM Campaign 是营销活动的标准实体，映射优惠券派发、限时折扣、新客礼包等活动，含预算、目标、效果统计 |
| 潜客/新客 | Lead | applicationCommon | 精确映射 | 通过平台（美团/抖音）触达但尚未消费的潜客，跟踪获取来源、意向等级、跟进状态 |
| 加盟商机 | Opportunity | applicationCommon | 精确映射 | 加盟商机管理，跟踪从意向→沟通→签约的全过程，含预计投资额、成交概率 |
| 营销名单 | MarketingList | applicationCommon | 精确映射 | 按条件筛选的客户分组，用于定向推送营销信息（如会员专享活动、沉睡客户召回） |
| 客户分群 | Segment | applicationCommon | 精确映射 | CDM Segment 将客户按 RFM 模型（最近消费/频率/金额）分层，支持精准营销 |
| 优惠券 | — | — | 概念映射 | CDM 无直接优惠券实体；可扩展自 foundationCommon 的 Discount/Promotion，或自定义 Coupon 实体 |
| 活动效果分析 | Campaign | applicationCommon | 近似映射 | Campaign 实体的活动指标字段（响应率、转化率、ROI）经扩展后满足效果分析需求 |
| 渠道/平台 | — | — | 概念映射 | 美团/抖音等外部渠道，映射至自定义 Channel 实体或通过 Account 的分类字段标识 |
| 客户标签/偏好 | — | — | 概念映射 | CDM 无直接客户标签实体；通过 Account 的扩展属性 + Tag 集合实现，支持自动打标和人工修正 |

### 2.5 D05 供应链域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 商品 | Product | foundationCommon | 精确映射 | CDM Product 是商品主数据，含名称、分类、规格、价格、单位；高岸中的茶叶/茶具/茶点均映射至此 |
| 商品分类 | ProductCategory | foundationCommon | 精确映射 | 商品分类层次结构，支持多级分类（茶叶→红茶/绿茶/普洱） |
| 计量单位 | UnitOfMeasure | foundationCommon | 精确映射 | 库存及销售计量单位（泡/罐/斤/份），支持单位间转换 |
| 价格表 | PriceList | foundationCommon | 精确映射 | 不同门店/时段的价格策略，含价目表头和明细行 |
| 采购单 | PurchaseOrder | operationsCommon | 精确映射 | 向供应商发起的采购请求，含商品明细、数量、单价、交货日期 |
| 采购单明细 | PurchaseOrderLine | operationsCommon | 精确映射 | PurchaseOrder 的行项目，逐条记录采购商品的详细信息 |
| 供应商 | Vendor | operationsCommon | 精确映射 | 映射所有对外付款的接收方，含供应商编号、资质、账期、评级 |
| 库存量 | InventoryOnHand | operationsCommon | 精确映射 | 实时库存数量，按商品+仓库维度记录，支持移动平均成本计算 |
| 库存调拨 | InventoryTransfer | operationsCommon | 精确映射 | 门店间商品调配，记录调出/调入方、商品明细、调拨原因 |
| 盘点单 | StockCount | operationsCommon | 精确映射 | 定期盘点记录，含盘点前数量、实盘数量、差异调整 |
| 仓库/门店库存 | Warehouse | operationsCommon | 精确映射 | 每个门店映射为一个 Warehouse 实体，管理与该门店相关的库存 |
| 供应商目录 | VendorCatalog | operationsCommon | 近似映射 | 供应商可提供的商品目录，含供货价、交货周期 |
| 批次号 | — | — | 概念映射 | CDM operationsCommon 无直接批次实体；参考 InventoryLot/SerialNumber 概念，自定义 Lot 实体与原 InventoryOnHand 关联 |
| 到期日/有效期 | — | — | 概念映射 | 通过 Product 实体的扩展属性（ExpiryDate）实现，食品类商品必填，到期自动冻结库存 |
| FIFO出库规则 | InventoryOnHand | operationsCommon | 近似映射 | 通过 InventoryOnHand 的批次维度和入库时间排序实现先进先出逻辑 |

### 2.6 D06 财务域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 会计科目 | MainAccount | operationsCommon | 精确映射 | CDM MainAccount 映射高岸的收支科目体系（一级/二级科目），决定财务报告的行项目归类 |
| 总账 | Ledger | operationsCommon | 精确映射 | 总账容器，按月结周期组织，每期月结生成一组凭证 |
| 预算 | Budget | operationsCommon | 精确映射 | 按门店/科目编制的经营预算，跟踪执行偏差，支持滚动预算 |
| 会计日历 | FiscalCalendar | operationsCommon | 精确映射 | 定义月结周期（上月25日至本月24日），控制过账期间开关 |
| 发票 | Invoice | foundationCommon | 精确映射 | 映射平台结算单（美团/抖音对账单）和系统发票；平台结算即为外部 Invoice |
| 发票明细 | InvoiceProduct | foundationCommon | 精确映射 | Invoice 的行项目，明细到每笔订单/商品的结算金额 |
| 付款 | Payment | operationsCommon | 近似映射 | 记录支出付款（请款/报销），含收款人、金额、付款方式、状态 |
| 付款计划 | PaymentSchedule | operationsCommon | 近似映射 | 分期支付的支出计划（如装修工程分期付款） |
| 汇率 | ExchangeRate | operationsCommon | 精确映射 | 若涉及跨境结算或多币种管理（目前未发生，预留） |
| 税码 | TaxCode | operationsCommon | 精确映射 | 映射商品/服务的税率（目前简化处理，仅记录税金支出，预留） |
| 币种 | Currency | operationsCommon | 精确映射 | 币种主数据（目前仅人民币，扩展预留） |
| 财务活动 | FinancialActivity | operationsCommon | 精确映射 | 每笔财务变动的原子记录，构成审计追溯的原始凭证 |
| 日结/月结 | — | — | 概念映射 | 高岸特有的批量结算操作；通过 FinancialActivity 的批量处理 + Ledger 的过账机制实现 |
| GL凭证（总账凭证） | JournalEntry | operationsCommon | 精确映射 | 每笔交易实时生成的借贷记账凭证，日结时汇总过账至 Ledger，月结时与明细账核对 |
| 应付账款（AP） | VendorPayment | operationsCommon | 近似映射 | 采购入库/费用审批通过后生成AP挂账（贷：应付账款），付款后核销（借：应付账款），与支出管理流程联动 |

### 2.7 D07 人力资源域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 员工 | Employee | operationsCommon | 精确映射 | 员工主数据，含姓名、岗位、入职日期、联系方式、合同信息 |
| 岗位 | Position | operationsCommon | 精确映射 | 组织结构中的岗位定义（店长/店员/财务/运营），每个岗位关联一个或多个员工 |
| 职位 | Job | operationsCommon | 精确映射 | 职位分类（管理层/执行层/实习生），决定薪资范围与职级 |
| 薪资 | Payroll | operationsCommon | 精确映射 | 薪资核算结果，按结算周期生成，含基本工资、绩效、扣款、实发 |
| 薪资明细 | Compensation | operationsCommon | 近似映射 | 薪资组成部分（基本工资、绩效奖金、加班费、餐补、社保扣款） |
| 考勤打卡 | — | — | 概念映射 | CDM 无直接考勤实体；概念映射至 operationsCommon 的 TimeOff 或自定义 Attendance 实体 |
| 员工技能 | Skill | operationsCommon | 精确映射 | 员工掌握的技能标签（茶艺师、保洁能手等），用于智能排班的技能匹配 |
| 绩效考核 | PerformanceReview | operationsCommon | 精确映射 | 周期性绩效评估记录，含评估维度、评分、评语、改进计划 |
| 员工档案 | Employee | operationsCommon | 精确映射 | Employee 实体已涵盖基本档案信息；附加信息（合同、证书等）通过扩展属性存储 |
| 排班 | — | — | 概念映射 | 高岸特有智能排班需求；可通过自定义 Shift/Schedule 实体实现 |

### 2.8 D08 技术域

| 高岸ERP概念 | CDM实体 | CDM所属组 | 映射类型 | 映射说明 |
|------------|---------|----------|---------|---------|
| 物联网设备 | Device | — | 概念映射 | CDM 的 Device 实体存在于 industryCommon/fieldService；高岸中需扩展，增加设备类型、通信协议、状态属性 |
| 用户账号 | User | applicationCommon | 精确映射 | 系统用户（店员、店长、财务、总部运营），用于身份认证与权限分配 |
| 操作审计 | AuditLog | applicationCommon | 精确映射 | CDM Audit 实体记录数据变更历史，映射至审计日志需求 |
| 系统任务 | SystemJob | applicationCommon | 近似映射 | 映射定时任务（日结、月结、自动对账等），跟踪执行状态 |
| 通知消息 | Activity | applicationCommon | 近似映射 | CDM Activity 是通用活动实体，映射系统通知、审批提醒、预警推送 |

---

## 3. 映射原则

1. **优先精确映射**：CDM 已有精确匹配的实体，优先直接复用，减少自定义开发
2. **扩展替代改造**：需适配高岸特有需求时，优先通过扩展属性（Extension）而非修改 CDM 核心定义
3. **概念映射兜底**：高岸特有概念（房态、智能排班、IoT设备等）通过自定义实体实现，但与 CDM 实体保持一致的关联模式

---

## 4. 修订历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始版本，提取自 REQ-01 V10.x 第2.5节的内容，含7大域共73个实体映射 |
| V1.1 | 2026-05-07 | 同步 REQ-01 V10.7 域结构调整：总部管理域→品牌运营域（D01），新增门店拓展域（D02），8域重排；门店与销售区域实体内迁至门店拓展域，新增设计图/施工图映射 |
