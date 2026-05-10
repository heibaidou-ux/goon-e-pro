"""
Reconstruct V10.7 MD file from V9.3 source + surviving V10.7 tail (Ch4-5+).
The corrupted file lost ~1370 lines from front matter through Ch3.3.
This script rebuilds the complete V10.7 document.
"""
import re

V93 = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.0，2026年5月6日）.md"
TAIL = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.7，2026年5月7日）_corrupted_tail.md"
OUTPUT = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.7，2026年5月7日）.md"

with open(V93, 'r', encoding='utf-8') as f:
    v93 = f.read()

with open(TAIL, 'r', encoding='utf-8') as f:
    tail = f.read()

# Find the start of Ch4 in the tail (line 176 = "## 第四章：非功能性需求")
ch4_start = tail.find("## 第四章：非功能性需求")

# ====================================================================
# FRONT MATTER
# ====================================================================
lines = []
lines.append("# 高岸茶室ERP系统需求说明书")
lines.append("")
lines.append("**版本**：V10.7")
lines.append("**日期**：2026年5月7日")
lines.append("**文档状态**：评审中")
lines.append("**编制依据**：")
lines.append("- 《高岸账务结算规范2025》")
lines.append("- 《金德店月度经营报告-2026年4月》")
lines.append("- 《月结操作规范》")
lines.append("- 《月结计算器》")
lines.append("- 面向对象建模方法论（方法论1、2、3、4）")
lines.append("- 《AI时代的平台型智能架构（企业经营版）V8.5》")
lines.append("- 高岸品牌第一次需求评审会议纪要（2026年5月3日）")
lines.append("- 20060501需求讨论结果")
lines.append("")
lines.append("---")
lines.append("")

# ====================================================================
# CHAPTER 1: 引言 (from V9.3 Ch1)
# ====================================================================

# Extract 1.1 项目背景
sec_1_1 = v93.find("### 1.1 项目背景")
sec_1_2 = v93.find("### 1.2 目标范围")
lines.append("## 第一章：引言")
lines.append("")
lines.append("### 1.1 项目背景")
lines.append("")
# Copy from V9.3 (skip the header line)
v93_1_1 = v93[sec_1_1:sec_1_2].strip()
# Skip the "### 1.1 项目背景" line
first_nl = v93_1_1.find("\n")
if first_nl != -1:
    v93_1_1 = v93_1_1[first_nl:].strip()
lines.append(v93_1_1)

# 1.2 目标范围
sec_1_3 = v93.find("### 1.3 业务术语")
section_1_2 = v93[sec_1_2:sec_1_3]

# Fix section numbering
section_1_2 = section_1_2.replace("#### 1.2.3 设计原则", "#### 1.2.2 设计原则")
section_1_2 = section_1_2.replace("#### 1.2.4 系统边界", "#### 1.2.3 系统边界")

lines.append("")
lines.append("### 1.2 目标范围")
lines.append("")
lines.append("#### 1.2.1 核心目标")
lines.append("")
# Extract core goals table
goals_start = v93.find("| 目标编号 | 目标 | 说明 |")
goals_end = v93.find("#### 1.2.3 设计原则")
lines.append(v93[goals_start:goals_end].strip())
lines.append("")
lines.append("所有其他功能（收支科目配置、多门店支持、报表导出、AI预警等）均为支撑上述两大目标而设。")
lines.append("")


lines.append("")
principles_start = v93.find("| 原则 | 说明 |", goals_end)
principles_end = v93.find("#### 1.2.4 系统边界")
lines.append(v93[principles_start:principles_end].strip())
lines.append("")

lines.append("#### 1.2.3 系统边界")
lines.append("")
boundary_start = v93.find("| 包含范围 | 不包含范围", principles_end)
boundary_end = v93.find("### 1.3 业务术语")
lines.append(v93[boundary_start:boundary_end].strip())

# 1.3 业务术语
lines.append("")
lines.append("### 1.3 业务全景")
lines.append("")

# Update business terminology table
sec_1_3_full = v93[sec_1_3:v93.find("### 1.4 业务域关系图")]

# Rename 1.3 to 1.4 and update the reference
sec_1_3_updated = sec_1_3_full.replace("### 1.3 业务术语", "#### 1.3.1 业务术语")
lines.append(sec_1_3_updated.strip())

# 1.4 Business domain relationship diagram
lines.append("")
lines.append("#### 1.3.2 业务域关系")
lines.append("")
sec_1_4 = v93.find("### 1.4 业务域关系图")
sec_2 = v93.find("## 第二章")
section_1_4 = v93[sec_1_4:sec_2]

# Remove the old heading
section_1_4 = section_1_4.replace("### 1.4 业务域关系图", "")
section_1_4 = section_1_4.replace("**域间关系说明**：", "**域间关系说明**：")
lines.append(section_1_4.strip())

lines.append("")

# ====================================================================
# CHAPTER 2: 总体结构 (new V10.x content, built from scratch)
# ====================================================================
lines.append("## 第二章：总体结构")
lines.append("")

# 2.1 业务域划分
lines.append("### 2.1 业务域划分")
lines.append("")
lines.append("系统按标准业务领域将全部功能划分为八个业务域，每个业务域对应一个组织部门，部门内的职能范围即该域在系统中的职责边界。")
lines.append("")

# V10.7 domain table (8 domains in new order)
domain_table = """| 编号 | 业务域 | 对应部门 | 核心职责 |
|------|--------|---------|---------|
| D01 | 品牌运营域 | 品牌运营部 | 品牌战略、加盟管理、运营标准、品牌运营看板、投资者关系 |
| D02 | 门店拓展域 | 拓展部 | 门店招标、选址评估、门店建设、门店配置与参数管理 |
| D03 | 门店运营域 | 运营部 | 门店日常经营、客户服务、房态管理、保洁任务、门店巡检 |
| D04 | 市场营销域 | 市场部 | 客户获取、营销活动、优惠券管理、渠道运营 |
| D05 | 供应链域 | 采购部/仓储部 | 商品采购、库存管理、供应商管理 |
| D06 | 财务域 | 财务部 | 收入管理、支出管理、月结对账、股东分红、报表体系 |
| D07 | 人力资源域 | 人事行政部 | 考勤管理、薪资核算、员工档案 |
| D08 | 技术域 | 技术部 | IoT设备管理、智能场景控制、系统运维、AI经营预警 |"""
lines.append(domain_table)
lines.append("")
lines.append("**域间关系说明**：各业务域通过统一的数据总线交换数据，不直接访问对方数据库。门店运营域为其他域提供业务事件驱动，财务域汇总各域产生的数据，技术域为门店运营域提供IOT自动化支撑。")
lines.append("")

# 2.1.1 组织架构
lines.append("#### 2.1.1 组织架构")
lines.append("")
lines.append("高岸品牌采用树形组织架构：")
lines.append("")
lines.append("- **根节点**：高岸总部（对应法人主体：高岸总公司）")
lines.append("- **一级节点**：各门店（对应法人主体：门店分公司或个体工商户）")
lines.append("- **二级节点**：门店下属部门（运营部、财务部、人事部等）")
lines.append("- **员工**：所有员工归属于某个部门")
lines.append("")
lines.append("**基础实体说明**：系统需建立以下基础数据实体——")
lines.append("- **公司**：法人主体，含公司名称、统一社会信用代码、法人代表、注册地址")
lines.append("- **法人**：法定代表人信息，关联公司实体")
lines.append("- **股东**：品牌股东/门店股东，含持股比例、出资额、关联公司")
lines.append("- **资金账户**：各法人主体名下的银行账户，含开户行、账号、账户类型（基本户/一般户/专户）")
lines.append("")
lines.append("各门店的财务独立核算，总部可查看全部门店合并报表。")
lines.append("")

# 2.2 子系统定义
lines.append("### 2.2 子系统定义")
lines.append("")
lines.append("每个业务域对应一个子系统，子系统负责该域的功能实现和数据管理。")
lines.append("")

subsystem_table = """| 子系统 | 对应业务域 | 主要用户 | 说明 |
|--------|-----------|---------|------|
| 品牌运营系统 | 品牌运营域 | 总部运营、投资人 | 品牌战略管理、加盟管理、运营标准制定、品牌运营看板、投资者关系 |
| 门店拓展系统 | 门店拓展域 | 总部拓展团队 | 门店招标、选址评估与审批、门店建设进度跟踪、门店配置管理 |
| 门店运营系统 | 门店运营域 | 店员、店长、客人 | 核心业务系统，处理预约、消费、房态等 |
| 营销系统 | 市场营销域 | 总部运营 | 活动创建、优惠券配置、效果分析 |
| 进销存系统 | 供应链域 | 店长、总部运营 | 采购、库存、供应商全链路管理 |
| 财务系统 | 财务域 | 财务、店长 | 月结、对账、分红、报表 |
| 人事系统 | 人力资源域 | 店长、总部 | 考勤、薪资、档案管理 |
| ERP支撑平台 | 技术域 | 系统管理员、技术运维 | ERP系统技术底座，含IoT设备管理、智能场景控制、AI经营预警引擎、系统日志与监控、运维管理 |"""
lines.append(subsystem_table)
lines.append("")
lines.append("**子系统协作说明**：")
lines.append("- 门店运营系统通过IoT平台提供的设备控制能力实现自动化")
lines.append("- 财务系统汇总门店运营系统、供应链系统、人事系统产生的业务数据")
lines.append("- 品牌运营系统依赖财务系统提供的数据进行品牌分析")
lines.append("- 营销系统通过门店运营系统执行活动策略")
lines.append("- 系统间通过统一的数据总线交换数据，不直接访问对方数据库")
lines.append("")

# 2.3 客户端应用视图
lines.append("### 2.3 客户端应用视图")
lines.append("")
lines.append("系统通过五个微信小程序和PC端覆盖不同角色的使用场景，各终端的功能分配如下：")
lines.append("")

terminal_table = """| 终端 | 使用角色 | 核心功能 | 使用方式 |
|------|---------|---------|---------|
| 客人端小程序 | 客人 | 包间预约、支付、商品购买、会员注册/充值/余额查询、优惠券查看、消费中续订/呼叫服务 | 微信小程序，扫码或搜索进入 |
| 店员端小程序 | 店员、店长 | 房态管理、保洁任务、对账工单、商品管理、库存操作、考勤打卡、门店巡检、IoT设备控制 | 微信小程序，店员账号登录 |
| 总部端小程序 | 总部运营、财务 | 各门店经营看板、收入/支出数据总览、月结报告查看、营销活动配置、预警通知 | 微信小程序，总部账号登录 |
| 加盟商端小程序 | 加盟投资人 | 加盟店经营数据查看、品牌管理费缴纳、总部通知公告、运营报表（简化视图） | 微信小程序，加盟商账号登录 |
| PC管理端 | 店长、财务、总部 | 报表深度分析、审批管理、基础数据配置、审计日志查看、系统管理 | PC浏览器 |

- 客人端是业务增长的核心入口，覆盖从引流到消费的全链路
- 店员端聚焦门店运营的移动化操作，默认展示工作台首页（待办事项、房态概览）
- 总部端面向多门店管理，提供综合数据看板和集中管控能力
- 加盟商端仅限查看本店数据，不可跨店访问"""
lines.append(terminal_table)
lines.append("")

# 2.4 CDM参考
lines.append("### 2.4 Microsoft CDM 实体映射参考")
lines.append("")
lines.append("系统参考 Microsoft Common Data Model（CDM）标准实体定义，各业务域的核心概念映射至 CDM 标准实体，以规范数据结构、保证可扩展性和便于系统对接。")
lines.append("")
lines.append("各业务域 CDM 实体映射概要：")
lines.append("")

cdm_table = """| 高岸业务域 | 主要CDM实体 | 实体数 | 匹配度 |
|-----------|------------|-------|-------|
| D01 品牌运营域 | Organization/BusinessUnit/Goal/GoalMetric | 8 | 近似映射为主 |
| D02 门店拓展域 | Account/Lead/Opportunity | 3 | 精确映射为主 |
| D03 门店运营域 | Account/Contact/Order/Appointment/Service/Task | 12 | 精确映射为主 |
| D04 市场营销域 | Campaign/Lead/Opportunity/MarketingList | 9 | 精确映射为主 |
| D05 供应链域 | Product/Supplier/Inventory/Procurement/Warehouse | 15 | 精确映射为主 |
| D06 财务域 | Ledger/Account/Invoice/JournalEntry/Budget | 14 | 近似映射为主 |
| D07 人力资源域 | Employee/Position/Schedule/Attendance/Payroll | 10 | 精确映射为主 |
| D08 技术域 | Device/SystemConfig/IoTAlert/AutomationRule | 5 | 概念映射为主 |"""
lines.append(cdm_table)
lines.append("")
lines.append("详细逐域实体映射说明（75个实体的精确映射/近似映射/概念映射标注）整理至独立文档《高岸ERP系统-CDM实体映射说明书》。")
lines.append("")

# ====================================================================
# CHAPTER 3: 业务域详细需求
# ====================================================================
lines.append("## 第三章：业务域详细需求")
lines.append("")

# Helper: extract table rows from V9.3 between two markers
def extract_table(v93_content, table_marker, end_marker):
    """Extract a markdown table from V9.3 content."""
    start = v93_content.find("| " + table_marker)
    if start == -1:
        start = v93_content.find("|" + table_marker)
    if start == -1:
        return None
    # Find the end of the table (double newline or another header)
    end = v93_content.find("\n\n", start)
    if end == -1:
        end = v93_content.find("\n## ", start)
    if end == -1:
        end = len(v93_content)
    return v93_content[start:end].strip()

def extract_section(v93_content, section_header, next_section_header=None):
    """Extract a section from V9.3 by header."""
    start = v93_content.find(section_header)
    if start == -1:
        return None
    if next_section_header:
        end = v93_content.find(next_section_header, start + len(section_header))
        if end == -1:
            end = len(v93_content)
    else:
        end = len(v93_content)
    return v93_content[start:end].strip()

# ---- D01: 品牌运营域 (from V9.3 4.12 - parts: 发展规划/品牌建设/运营看板/投资者关系) ----
lines.append("### 3.1 品牌运营域")
lines.append("")
lines.append("品牌运营域是品牌的决策中枢，负责制定品牌发展战略、建设品牌标准体系、管理加盟体系与投资者关系。从系统开发视角，该域提供支撑品牌管控职能的业务模块，包括发展规划、品牌建设、品牌运营看板、投资者关系。各业务模块中涉及的审批流程均通过统一的工作流引擎驱动（详见 4.7 节）。")
lines.append("")

# 3.1.1 发展规划 (from V9.3 4.12 发展规划部分)
lines.append("#### 3.1.1 发展规划")
lines.append("")
mulsection = extract_section(v93, "### 4.12 多门店与总部管理域（MUL）", "## 第五章")
# Extract the content before 门店拓展 section
if mulsection:
    dev_start = mulsection.find("**功能点**：")
    dev_end = mulsection.find("#### 4.12.2 品牌建设")
    if dev_start != -1 and dev_end != -1:
        dev_content = mulsection[dev_start:dev_end].strip()
        # Remove the "参考流程" section reference 3.1.5
        dev_content = dev_content.replace("| **参考流程** | [门店拓展泳道图见3.1.5节](#315-门店拓展) |", "")
        lines.append("总部制定品牌中长期发展目标与经营计划，统筹门店拓展规划，跟踪战略执行进度，确保品牌持续健康发展。")
        lines.append("")
        lines.append("**功能点**：")
        lines.append("- 目标管理体系：经营目标设定（营收、利润、门店数量、会员目标）；目标分解下达（年度/月度分解至门店，支持滚动调整）；目标进度跟踪（关键指标看板，偏差自动预警）")
        lines.append("- 门店拓展规划：区域布局规划（目标城市、门店密度、直营/加盟占比策略）；规划执行跟踪（已开店vs计划量对比，进度看板）；市场容量评估（竞品分析、品类渗透率，支持外部数据接入）")
        lines.append("- 战略执行：里程碑管理（重大事项如品牌升级、市场进入、组织调整的计划与跟踪）；经营复盘报告（定期战略回顾，调整建议）")
        lines.append("")
    else:
        lines.append("总部制定品牌中长期发展目标与经营计划，统筹门店拓展规划，跟踪战略执行进度。")
        lines.append("")
        lines.append("**功能点**：目标管理体系、门店拓展规划、战略执行跟踪")
        lines.append("")

# 3.1.2 品牌建设
lines.append("#### 3.1.2 品牌建设")
lines.append("")
lines.append("统一管理品牌标准、视觉资产和品牌制度，支撑品牌输出一致性。")
lines.append("")
lines.append("**功能点**：")
lines.append("- 品牌标准管理：品牌定位文档（品牌价值主张）；视觉识别系统（VI规范归档及版本管理）；空间设计标准手册")
lines.append("- 品牌资产库：品牌数字资产（Logo、标准色、字体、品牌元素模板）；资产使用审批（下载、使用申请、审批授权）；资产使用追踪（记录哪些门店使用了哪些资产及时间）")
lines.append("- 品牌制度设计：运营标准手册、服务标准手册、员工行为规范（制定与发布）；品牌执行检查（门店巡检含标识规范、物料使用等合规项抽查）")
lines.append("- 新品牌入驻（未来扩展）：新品牌创建、品牌配置清单、品牌切换")
lines.append("")

# 3.1.3 品牌运营看板
lines.append("#### 3.1.3 品牌运营看板")
lines.append("")
lines.append("总部实时查看全品牌经营数据，支持跨店对比和决策分析。")
lines.append("")
lines.append("**功能点**：")
lines.append("- 全品牌总览：营收、支出、利润、客流量、各店占比")
lines.append("- 门店经营数据对比：收入/支出/利润/客流/客单价")
lines.append("- 趋势分析：月度趋势、同比/环比")
lines.append("- 门店经营健康度评分（基于营收、成本、客流、巡检等综合指标）")
lines.append("- 异常门店自动标红")
lines.append("")
lines.append("**看板模板（示例）**：")
lines.append("")
lines.append("| 维度 | 指标 | 门店A | 门店B | 门店C | 目标值 |")
lines.append("|------|------|-------|-------|-------|-------|")
lines.append("| 营收 | 月营收（万元） | 12.5 | 8.6 | 5.2 | 10.0 |")
lines.append("| 营收 | 同比增长率 | +15% | +8% | -3% | +10% |")
lines.append("| 成本 | 成本率 | 42% | 48% | 55% | 45% |")
lines.append("| 客流 | 月新客数（人次） | 120 | 85 | 45 | 100 |")
lines.append("| 客单 | 平均客单价（元） | 156 | 128 | 142 | 150 |")
lines.append("| 会员 | 活跃会员数 | 280 | 165 | 89 | 200 |")
lines.append("| 效率 | 综合评分 | 92 | 78 | 65 | 85 |")
lines.append("")

# 3.1.4 投资者关系
lines.append("#### 3.1.4 投资者关系")
lines.append("")
lines.append("投资人查看投资门店的财务数据和分红记录。")
lines.append("")
lines.append("**功能点**：")
lines.append("- 投资门店列表（用户投资的门店、持股比例）")
lines.append("- 财务看板：实时营收、门店利润排名（仅限投资门店）、近6个月利润趋势图")
lines.append("- 分红记录查看（历史分红明细、到账状态）")
lines.append("- 重大告警推送（设备批量离线、客流异常、对账大额差异）")
lines.append("")
lines.append("**业务约束**：")
lines.append("- 投资人仅可查看自己投资的门店数据")
lines.append("- 财务看板数据基于已确认的月结报告，非实时流水")
lines.append("- 重大告警实时推送（不依赖月结周期）")
lines.append("")
lines.append("**投资者关系看板（示例）**：")
lines.append("")
lines.append("| 我的投资 | 投资门店数 | 总投资金额 | 累计分红 | 收益率 |")
lines.append("|---------|-----------|-----------|---------|-------|")
lines.append("| 数据 | 3家 | 25.0万 | 3.8万 | 15.2% |")
lines.append("")
lines.append("| 投资门店详情 | 持股比例 | 月营收 | 月利润 | 累计分红 | 经营状态 |")
lines.append("|-------------|---------|-------|-------|---------|---------|")
lines.append("| 盈丰店 | 30% | 12.5万 | 2.8万 | 1.5万 | 正常 |")
lines.append("| 金德店 | 20% | 8.6万 | 1.5万 | 0.8万 | 正常 |")
lines.append("")

# ---- D02: 门店拓展域 (from V9.3 4.12 门店拓展+门店配置 parts) ----
lines.append("### 3.2 门店拓展域")
lines.append("")
lines.append("门店拓展域负责品牌门店网络的规划、选址、建设与配置管理。从系统开发视角，该域管理门店从选址到开业的全过程，确保门店布局符合品牌战略、建设标准统一、运营参数规范配置。各业务模块中涉及的审批流程均通过统一的工作流引擎驱动（详见 4.7 节）。")
lines.append("")

# 3.2.1 门店选址与建设
lines.append("#### 3.2.1 门店选址与建设")
lines.append("")
lines.append("总部从选址到建设完成的全过程管理，支持投资者参与和不参与两种模式，记录门店建设投资，建设完成后自动转固。")
lines.append("")
lines.append("**门店来源渠道**：")
lines.append("- 店长推荐：在职店长利用本地资源推荐选址")
lines.append("- 加盟商提供：加盟商自行寻找并推荐")
lines.append("- 总部物色：总部拓展团队自主选址")
lines.append("")
lines.append("**功能点**：")
lines.append("- **门店选址与投资者参与模式**：")
lines.append("  - 选址信息上报（来源备注、商圈、地址、面积、周边环境、推荐理由）")
lines.append("  - 投资者看店（投资者实地看店后录入评价）")
lines.append("  - 投资者意向确认（投资者确认投资意向和投资金额）")
lines.append("  - 选址审批（总部评审 → 总经理批准）")
lines.append("  - 选址历史记录查询")
lines.append("- **门店建设**：")
lines.append("  - 建设费用归集（装修工程费、设备采购费、家具采购费、人工费等分项记录）")
lines.append("  - 建设进度跟踪（分阶段里程碑、时间节点、验收记录、施工单位信息）")
lines.append("  - 建设完成后自动转固（转固后不可修改，转为历史存档）")
lines.append("  - 转固后建设总成本归集至门店的固定资产台账")
lines.append("- **集中审批**：所有超出门店权限的申请自动汇集至总部集中审批列表，支持审批详情查看（申请内容、历史审批链、附件）、审批操作（通过/驳回/退回补充）、操作留痕、超时告警（超48小时未处理推送提醒）")
lines.append("")
lines.append("**设计图与施工图管理**：")
lines.append("- 系统支持门店空间设计图、施工图、水电图的在线绘制与版本管理")
lines.append("- 设计参数模板化：门店面积、包间数量、设施配置等参数输入后，系统辅助生成标准空间布局方案")
lines.append("- 设计审批流程：设计图提交后经总部评审确认方可进入施工阶段")
lines.append("- 设计变更管理：施工过程中的设计变更须重新提交审批，变更历史完整留痕")
lines.append("- 图纸归档：完工后所有设计图、施工图、竣工图归档至对应门店的资产档案，支持后续查询与改造参考")
lines.append("")

# 3.2.2 门店配置
lines.append("#### 3.2.2 门店配置")
lines.append("")
lines.append("总部统一管理各门店的经营参数和基础数据配置。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **门店基本信息**：")
lines.append("  - 门店创建与信息维护（名称、地址、电话、营业时间、门店类型：直营/加盟）")
lines.append("  - 门店状态管理（营业中/暂停营业/装修中/已关闭）")
lines.append("  - 门店经营参数配置（结算周期、配送费规则、保洁超时升级阈值）")
lines.append("- **空间管理**：")
lines.append("  - 空间创建与配置（名称、照片、容纳人数、设施类型、价格体系）")
lines.append("  - 空间状态管理（空闲/使用中/待打扫/维护中）")
lines.append("  - 设施标注（投影仪、音响、舞台、K歌设备等）")
lines.append("- **基础数据配置**：")
lines.append("  - 收支科目体系配置（一级科目、二级科目、适用门店）")
lines.append("  - 支付方式配置（微信/支付宝/会员余额，可按门店独立启用/关闭）")
lines.append("  - 审批流程配置（审批路由、金额阈值、审批节点）")
lines.append("  - 通用运营参数配置（营业时间模板、计费单位、超时策略）")
lines.append("")

# ---- D03: 门店运营域 (from V9.3 4.2 客人消费域 + 4.7 巡检域) ----
lines.append("### 3.3 门店运营域")
lines.append("")
lines.append("门店运营域是品牌的核心业务域，覆盖客人从预约到退房的全流程消费体验、商品零售、房态管理、保洁任务和门店巡检。")
lines.append("")

# 3.3.1 包间预约与消费
lines.append("#### 3.3.1 空间租用（包间预约与消费）")
lines.append("")
lines.append("客人通过小程序选择门店、空间、时段，在线支付后系统自动确认预约、下发门禁密码并联动IoT设备。")
lines.append("")
lines.append("**前置条件**：客人已登录小程序（支持微信一键登录，无需注册）；所选门店在营业时间内；所选空间在目标时段内空闲。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 客人进入小程序首页，选择目标门店（展示门店图片、评分、距离）")
lines.append("2. 选择空间（展示空间图片、容纳人数、价格、设施说明）")
lines.append("3. 选择日期和时段（以30分钟为单位，展示可预约时段）")
lines.append("4. 确认订单信息，选择支付方式（微信/支付宝/会员余额）")
lines.append("5. 支付成功 → 系统生成预约单")
lines.append("6. 系统自动生成临时门禁密码（支持离线动态密码方案）")
lines.append("7. 发送预约成功通知（门禁密码、使用指引）")
lines.append("8. 预约开始前5分钟，系统下发预冷/预热指令给IoT平台")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 预约范围：当前时间+2小时至30天内")
lines.append("- 预约最小单位：30分钟")
lines.append("- 超时取消：到达预约时间30分钟未开门，系统自动取消预约并释放空间")
lines.append("- 取消政策：预约开始时间前2小时以上免费取消；2小时内取消收取50%费用；超时取消全额收取")
lines.append("- 续订规则：使用中可通过小程序续订（延长时段并支付差价），每次续订最少1小时")
lines.append("- 同一时段同一空间不可重复预约")
lines.append("")
lines.append("**异常处理**：")
lines.append("- 支付成功但系统异常 → 无法确认订单时标记为“人工处理”，通知店长")
lines.append("- 门禁密码下发失败 → 店员通过远程控制手动开门")
lines.append("- 预约时段IoT设备故障 → IoT平台告警，推送店员处理")
lines.append("")

# 3.3.2 商品零售
lines.append("#### 3.3.2 商品零售")
lines.append("")
lines.append("客人通过小程序在线点单购物（茶叶、茶点、茶具、套餐），支持自提及外卖配送。")
lines.append("")
lines.append("**前置条件**：商品已上架且有库存；自提需在营业时间内；外卖配送范围内。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 浏览商品分类（茶叶/茶点/茶具/套餐），支持搜索和筛选")
lines.append("2. 查看商品详情（图片、价格、规格说明）")
lines.append("3. 加入购物车或直接购买")
lines.append("4. 选择配送方式（自提/外卖），外卖需填写地址并计算运费")
lines.append("5. 确认订单并支付")
lines.append("6. 自提：生成取货码，到店核销；外卖：店员发货")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 商品支持多种规格（茶叶可按泡/罐/斤计价）")
lines.append("- 实时扣减库存，库存不足时自动停止下单")
lines.append("- 配送费规则可配置（满免/固定/按距离）")
lines.append("")
lines.append("**异常处理**：")
lines.append("- 支付成功但库存不足 → 系统锁定库存，若确认无货则退款")
lines.append("- 外卖未及时取货 → 超过48小时未取自动退款")
lines.append("")

# 3.3.3 房态管理
lines.append("#### 3.3.3 房态管理")
lines.append("")
lines.append("店员/店长实时查看所有空间状态（空闲/使用中/待打扫/维护），支持远程控制设备。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 进入房态管理页面（平面图/列表两种视图）")
lines.append("2. 查看各空间状态（颜色区分：绿色=空闲、蓝色=使用中、黄色=待打扫、红色=维护）")
lines.append("3. 点击空间查看详情（当前订单信息、剩余时间、设备状态）")
lines.append("4. 远程控制操作（开门、调温、关灯、强制退房），需填写操作原因并关联工单ID")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 空间状态由系统自动更新（开门→使用中，退房→待打扫，保洁完成→空闲）")
lines.append("- 远程控制记录自动写入操作日志（操作人、时间、操作内容、原因）")
lines.append("- 强制退房须填写原因并关联工单ID记录审计日志")
lines.append("")
lines.append("**异常处理**：")
lines.append("- 远程控制失败 → 提示设备离线状态，建议店员手动操作")
lines.append("")

# 3.3.4 保洁任务
lines.append("#### 3.3.4 保洁任务")
lines.append("")
lines.append("客人退房后系统自动生成保洁任务，指派当值店员。超时未接单通知店长。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 系统自动生成保洁任务（含空间名称、退房时间、清洁要求）")
lines.append("2. 推送至店员端（按时间顺序排列，超时高亮）")
lines.append("3. 店员接单 → 到达空间 → 开始清洁 → 完成清洁")
lines.append("4. 店员点击“完成”，系统更新空间状态为“空闲”")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 超时定义：退房后30分钟未接单，推送提醒至店长")
lines.append("- 清洁中不可预订，完成后自动释放")
lines.append("- 完成清洁需店员手动确认，系统不自动判定")
lines.append("")
lines.append("**异常处理**：")
lines.append("- 店员超时未接单（30分钟）→ 店长收到提醒，重新指派")
lines.append("- 清洁中发现设备故障 → 店员在保洁页面标记异常，自动生	成设备维修工单")
lines.append("")

# 3.3.5 巡店管理
lines.append("#### 3.3.5 巡店管理")
lines.append("")
lines.append("店长/店员按巡检模板检查门店经营状况和安全状况，异常项自动创建整改工单。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **巡检模板配置**：总部配置巡检模板（经营检查+安全检查），每日/每周/每月自动生成任务")
lines.append("  - 经营检查项：服务质量、人员到岗、商品陈列、环境卫生、仪容仪表")
lines.append("  - 安全检查项：消防设备、电器安全、疏散通道、监控设备、门锁状态")
lines.append("- **巡检执行**：逐项检查（正常/异常），异常需拍照并填写说明")
lines.append("- **整改工单**：店长审核巡检报告，对异常项创建整改工单，指派责任人跟踪至关闭")
lines.append("- **巡检统计**：各店巡检完成率、异常项分类统计、平均整改时长")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 巡检频率可配置，默认每日一次")
lines.append("- 超时12小时未完成升级提醒店长")
lines.append("- 连续3次巡检完成率<80%自动告警总部")
lines.append("")

# ---- D04: 市场营销域 (from V9.3 4.1 营销域) ----
lines.append("### 3.4 市场营销域")
lines.append("")
lines.append("市场营销域管理所有市场推广活动、优惠券发放核销和客户获取渠道分析，是业务增长的起点。")
lines.append("")

# 3.4.1 营销活动
lines.append("#### 3.4.1 营销活动")
lines.append("")
lines.append("总部运营创建营销活动，支持多种活动类型，审批通过后自动同步至第三方平台。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 总部运营进入营销管理模块，点击“创建活动”")
lines.append("2. 选择活动类型：限时折扣/满减优惠/新客礼包/充值赠送/会员专享")
lines.append("3. 配置活动参数（活动名称、时间范围、折扣力度、适用商品范围、适用门店、目标人群）")
lines.append("4. 设置活动预算上限和风控规则")
lines.append("5. 提交审批（经审批流后活动自动生效）")
lines.append("6. 审批通过后活动自动生效，系统同步至各平台（美团、抖音、小程序）")
lines.append("7. 活动期间实时展示数据（曝光量、参与量、核销量、优惠金额）")
lines.append("8. 活动结束后自动归档，生成效果分析报告")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 同一商品同一时段不可叠加多个活动")
lines.append("- 活动预算超支时自动暂停")
lines.append("- 活动信息可修改（仅限未开始的活动）")
lines.append("- 活动涉及价格变动的，必须在系统内创建并同步至平台，严禁在平台侧直接修改价格")
lines.append("")

# 3.4.2 优惠券管理
lines.append("#### 3.4.2 优惠券管理")
lines.append("")
lines.append("系统支持创建和发放优惠券，客人领取后可在下单时抵扣。核销后根据消费行为自动打标签，积累消费画像用于精准营销。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 创建优惠券模板（类型：满减券/折扣券/现金券/赠品券）")
lines.append("2. 配置面额、使用门槛、有效期、适用商品范围")
lines.append("3. 选择发放方式：")
lines.append("   - 新会员注册自动发放（新人礼包）")
lines.append("   - 充值后赠送")
lines.append("   - 消费后赠送")
lines.append("   - 手动定向发放（指定会员或人群）")
lines.append("4. 客人领取后存入账户，下单时自动匹配可用优惠券")
lines.append("5. 核销后记录使用明细，根据核销行为自动更新客户标签")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 优惠券不可叠加使用，一笔订单限用一张")
lines.append("- 过期优惠券自动失效")
lines.append("- 退单时优惠券按规则退回（若仍在有效期内）")
lines.append("- 优惠券核销数据纳入营销费用核算")
lines.append("")
lines.append("**客户标签闭环**：核销后系统根据消费行为自动更新客户标签（如“价格敏感型”“特定时段活跃”“高客单价”），积累消费画像用于后续精准营销。")
lines.append("")

# ---- D05: 供应链域 (from V9.3 4.10 采购与库存域) ----
lines.append("### 3.5 供应链域")
lines.append("")
lines.append("供应链域覆盖商品采购、库存管理和供应商管理全链路，保障门店运营所需物资的及时供应。")
lines.append("")

# 3.5.1 采购管理
lines.append("#### 3.5.1 采购管理")
lines.append("")
lines.append("门店发起采购申请，经审批后形成采购订单，到货后验收入库。")
lines.append("")
lines.append("**前置条件**：采购商品已维护至系统；供应商信息已注册。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 店员/店长发起采购申请（可基于库存预警自动生成建议采购单）")
lines.append("2. 选择商品、数量、供应商，填写期望到货日期")
lines.append("3. 提交审批（金额路由：<500元店长审批；500-5000元店长+财务；>5000元店长+财务+总部）")
lines.append("4. 审批通过后生成采购订单")
lines.append("5. 通知供应商发货（系统可打印采购单发送给供应商）")
lines.append("6. 到货后验收入库，系统记录实际到货数量")
lines.append("7. 生成入库单，更新库存")
lines.append("")
lines.append("**异常处理**：")
lines.append("- 到货数量与采购数量不一致 → 差异记录，支持部分入库")
lines.append("- 商品质量不合格 → 退货并重新采购")
lines.append("")

# 3.5.2 库存管理
lines.append("#### 3.5.2 库存管理")
lines.append("")
lines.append("系统管理各门店的商品库存，支持入库、出库、盘点、调拨全流程，并提供库存预警和批次追踪。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **库存台账**：按门店、商品SKU展示实时库存数量，支持查看出入库流水")
lines.append("- **入库管理**：采购到货入库、退货入库、调拨入库，记录批次号和有效期")
lines.append("- **出库管理**：销售出库（自动扣减）、调拨出库、报损出库")
lines.append("- **库存盘点**：店长发起盘点任务，系统生成盘点清单，店员逐项清点实物并录入，差异（盘盈/盘亏）经审批后调整台账")
lines.append("- **库存调拨**：门店间商品调拨，发起调拨申请→调出店出库→调入店入库，支持跨店审批")
lines.append("- **批次追踪与有效期管理**：入库时记录生产日期/批次号/有效期，出库时FIFO（先进先出）校验，到期前30天自动预警")
lines.append("- **库存预警**：低于安全库存阈值自动生成补货提醒，支持按商品独立配置阈值")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 库存变动实时更新，每笔出入库均记录操作人、时间、数量、原因")
lines.append("- 盘点差异须店长审批，盘亏报损需说明原因")
lines.append("- 调拨在途商品不纳入双方门店可用库存")
lines.append("- 到期商品系统自动锁定不可销售")
lines.append("")

# 3.5.3 供应商管理
lines.append("#### 3.5.3 供应商管理")
lines.append("")
lines.append("所有对外付款的接收方纳入供应商库统一管理，请款/报销时必须从供应商库中选择。")
lines.append("")
lines.append("**功能点**：")
lines.append("- 供应商信息管理：编号、名称、类型（商品供应商/场地出租方/广告服务商/人力服务商/固定资产供应商/其他）、联系人、电话、银行账户、税号、付款条件（月结/现结/预付）")
lines.append("- 请款或报销必须从供应商库中选择")
lines.append("- 供应商支持启用/禁用")
lines.append("- 供应商历史交易查询")
lines.append("")

# ---- D06: 财务域 (from V9.3 4.3 + 4.4 + 4.6 + Ch5) ----
lines.append("### 3.6 财务域")
lines.append("")
lines.append("财务域是系统的核心数据汇聚域，负责收入归集、支出管理、月结对账、股东分红和报表输出，确保财务数据的准确性和完整性。")
lines.append("")

# 3.6.1 收入管理
lines.append("#### 3.6.1 收入管理")
lines.append("")
lines.append("系统自动归集所有收入，按标准科目框架分类。收入按主体分为总部收入和门店收入两大类别。")
lines.append("")

revenue_table = """| 收入主体 | 一级科目 | 二级科目 | 来源 |
|---------|---------|---------|------|
| **总部** | 主营业务收入 | 品牌特许经营收入（加盟金） | 加盟合同签约 |
| **总部** | 主营业务收入 | 品牌管理费 | 加盟店年度管理费 |
| **总部** | 主营业务收入 | 设计费 | 门店空间设计服务 |
| **总部** | 主营业务收入 | 供应链收入（茶叶销售） | 向各门店销售茶叶/茶具 |
| **门店** | 主营业务收入 | 空间租用收入 | 包间/空间租用订单 |
| **门店** | 主营业务收入 | 商品零售收入 | 零售订单 |
| **门店** | 其他业务收入 | 平台补贴收入 | 平台结算单 |
| **门店** | 其他业务收入 | 充电宝分成 | 供应商结算 |
| **门店** | 其他业务收入 | 广告收入 | 合同确认 |
| **门店** | 其他业务收入 | 赔偿金 | 偶发收入 |
| **门店** | 债务性收入 | 会员充值 | 充值记录（递延确认） |"""
lines.append(revenue_table)
lines.append("")
lines.append("**功能点**：")
lines.append("- 空间租用收入：退房时自动按实际使用时长或套餐固定金额计算，生成收入流水")
lines.append("- 零售商品收入：商品订单完成支付后自动生成收入流水，同步扣减库存")
lines.append("- 会员充值：充值时不确认为营业收入，记为预收账款（债务性收入），消费时转入主营业务收入")
lines.append("- 其他业务收入：充电宝分成、赔偿金等偶发收入支持手工录入，需上传凭证")
lines.append("- 每日凌晨自动汇总前一日所有已完成订单，按门店、业务类型、支付方式分组统计，生成日结凭证")
lines.append("")

# 3.6.2 支出管理
lines.append("#### 3.6.2 支出管理")
lines.append("")
lines.append("管理所有对外付款，涵盖请款（事前）、报销（事后）和自动归集支出。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **请款申请（事前）**：填写用途、预估金额、收款供应商、期望付款日期，上传附件（合同/报价单），提交后启动审批流")
lines.append("- **报销申请（事后）**：填写费用明细、金额、发生日期，上传凭证（发票/收据/平台截图），提交后启动审批流")
lines.append("- **广告费自动归集**：系统每月定时从美团、抖音广告后台拉取广告消耗金额，生成支出记录")
lines.append("- **固定支出录入**：房租、水电、物业费等由总部或店长手工录入，需上传合同或账单")
lines.append("- **薪资导入**：每月薪资Excel导入，系统自动计算实发工资并生成人力成本支出")
lines.append("- **管理费用分摊**：总部管理费用月末按各店营收占比自动分摊至门店")
lines.append("")
lines.append("**支出科目框架**：广告费、场地成本、人力成本、采购成本、资产折旧、管理费用、税费、其他")
lines.append("")
lines.append("**审批路由**：<500元店长审批；500-5000元店长+财务会签；>5000元店长+财务+总部会签（后台可配置）")
lines.append("")

# 3.6.3 自动月结
lines.append("#### 3.6.3 自动月结")
lines.append("")
lines.append("每月25日自动结算上月25日至本月24日的经营数据，生成月结报告。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 每月25日凌晨自动触发月结流程")
lines.append("2. 汇总期内所有已完成订单的收入数据，按科目分类")
lines.append("3. 汇总期内所有支出数据，按科目分类")
lines.append("4. 自动计提当月固定资产折旧")
lines.append("5. 自动分摊总部管理费用")
lines.append("6. 计算各门店利润 = 收入 - 支出 - 折旧 - 分摊费用")
lines.append("7. 生成月结报告（损益汇总、收入明细、支出明细）")
lines.append("8. 集团合并报表（汇总各门店数据）")
lines.append("9. 推送报告至相关方（店长、财务、总部、投资人）")
lines.append("")
lines.append("**月结报告结构（Excel输出）**：")
lines.append("")
lines.append("**工作表1：收入明细**")
lines.append("")
lines.append("| 字段 | 说明 | 数据来源 |")
lines.append("|------|------|---------|")
lines.append("| 门店名称 | 高岸分店 | 系统门店信息 |")
lines.append("| 日期 | 日结日期 | 系统日结记录 |")
lines.append("| 订单编号 | 系统订单号 | ERP订单系统 |")
lines.append("| 平台 | 美团/抖音/支付宝/微信/现金 | 支付渠道 |")
lines.append("| 商品/服务 | 具体消费项目 | 订单明细 |")
lines.append("| 订单金额 | 客人下单总金额 | 订单金额 |")
lines.append("| 平台优惠 | 平台承担优惠 | 平台结算单 |")
lines.append("| 商家优惠 | 商家承担优惠 | ERP优惠券系统 |")
lines.append("| 平台服务费 | 平台抽成 | 平台结算单 |")
lines.append("| 达人佣金 | 达人带货分成（仅抖音） | 抖音结算单 |")
lines.append("| 实收金额 | 最终到账金额 | 平台结算单 |")
lines.append("| 支付时间 | 实际支付时间 | 支付回调 |")
lines.append("| GL凭证号 | 关联会计凭证号 | GL系统 |")
lines.append("")
lines.append("**工作表2：支出明细**")
lines.append("")
lines.append("| 字段 | 说明 | 数据来源 |")
lines.append("|------|------|---------|")
lines.append("| 门店名称 | 高岸分店 | 系统门店信息 |")
lines.append("| 日期 | 支出日期 | 支出单据 |")
lines.append("| 单据编号 | 申请单号/报销单号 | 支出管理系统 |")
lines.append("| 支出科目 | 一级/二级科目 | 科目表配置 |")
lines.append("| 供应商/收款人 | 收款方名称 | 供应商/员工信息 |")
lines.append("| 金额 | 含税金额 | 支出单据 |")
lines.append("| 税率 | 增值税率 | 税务配置 |")
lines.append("| 不含税金额 | 税前金额 | 自动计算 |")
lines.append("| 税额 | 增值税额 | 自动计算 |")
lines.append("| 支付方式 | 对公转账/备用金/报销 | 支付方式 |")
lines.append("| 支付状态 | 已支付/待支付/审批中 | 支出管理 |")
lines.append("| GL凭证号 | 关联会计凭证号 | GL系统 |")
lines.append("")
lines.append("**工作表3：损益汇总**")
lines.append("")
lines.append("| 字段 | 金额 | 说明 |")
lines.append("|------|------|------|")
lines.append("| 营业收入 | 汇总 | 各平台实收金额 + 线下收款 |")
lines.append("| 减：平台服务费 | 汇总 | 各平台抽成合计 |")
lines.append("| 减：营销费用 | 汇总 | 优惠券补贴 + 满减活动 |")
lines.append("| 减：原材料成本 | 汇总 | 当期消耗物料成本 |")
lines.append("| 减：人力成本 | 汇总 | 工资 + 社保 + 公积金 |")
lines.append("| 减：折旧费用 | 汇总 | 固定资产折旧 |")
lines.append("| 减：运营费用 | 汇总 | 房租、水电、物业等 |")
lines.append("| 营业利润 | = 收入 - 各项费用 | — |")
lines.append("| 加：平台补贴收入 | 汇总 | 平台营销补贴 |")
lines.append("| 加：品牌特许经营收入 | 汇总 | 加盟金/品牌管理费 |")
lines.append("| 净利润 | = 营业利润 + 补贴 + 特许收入 | — |")
lines.append("")

# 3.6.4 智能对账
lines.append("#### 3.6.4 智能对账")
lines.append("")
lines.append("系统在实时、日结、月结三个层级自动对账，确保收入数据准确。差异工单自动创建并推送处理。")
lines.append("")
lines.append("**收入渠道对账口径**：")
lines.append("")
income_channel_mapping = """| 收入渠道 | 对账口径 | 查询路径 |
|---------|---------|---------|
| 美团茶室-团购 | 按打款记录录账，结算周期内 | 美团开店宝（非餐饮版）> 打款记录 |
| 美团CAFE-团购 | 按商家应得录账，结算周期内 | 美团开店宝（餐饮版）> 每日收益 |
| 美大收钱码 | 次日到账，查询上月24日～本月23日 | 美团开店宝 > 收钱助手 |
| 抖音券 | 周期性到账，按商家应得录账 | 抖音来客 > 到账与收益 |
| 高德券 | 待调研（优先API，否则手工导入） | 高德平台 |
| 茗匠结算 | 次日到账，查询上月24日～本月23日 | 汇旺财 > 结算查询 |
| 微信支付（直连） | API自动，T+1到账 | 微信商户平台 |
| 会员余额消费 | 系统内部自动，消费时转营收 | ERP内部账户 |
| 银行转账 | 半自动，导入银行流水 | 银行对账单 |
| 现金 | 手工录入，现金转微信后核销 | 门店日报 |
| 公账收入 | 手工录入，财务确认 | 财务确认 |
| 充电宝租赁分成 | 美团开店宝充电宝模块，手工确认 | 美团开店宝 |
| 平台补贴收入 | 按平台结算单确认 | 各平台结算中心 |"""
lines.append(income_channel_mapping)
lines.append("")
lines.append("**对账说明**：")
lines.append("- 美团“茶室”类目与“CAFE”类目的结算科目不同，茶室类目按“房间费+商品费”合并结算，CAFE类目按单品结算")
lines.append("- 抖音结算单含订单金额、平台佣金、达人佣金、平台补贴四项，需分别入账")
lines.append("- 各平台均为T+1结算周期（美团结算周期为14天自动/可手工提现）")
lines.append("- 月结时以各平台结算单汇总金额与系统收入流水进行汇总比对（总额对账），确保账实一致")
lines.append("")
lines.append("**差异类型**：")
lines.append("- 平台金额不一致：订单金额与平台结算金额不同")
lines.append("- 平台有系统无：平台有订单但ERP未记录")
lines.append("- 系统有平台无：ERP有订单但平台无记录")
lines.append("- ERP内部异常：未消费而收了钱、消费了却没收到钱、销售产品与收入金额不相符且无合理说明")
lines.append("")
lines.append("**对账提醒**：")
lines.append("- 实时差异通过小程序订阅消息立即推送给当班店员")
lines.append("- 日结差异汇总推送给店长")
lines.append("- 月结未处理工单升级推送给财务")
lines.append("")

# 3.6.5 股东分红
lines.append("#### 3.6.5 股东分红")
lines.append("")
lines.append("系统根据持股比例自动计算分红，支持品牌股东和门店股东两种类型。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **品牌股东**：持有高岸品牌股份，按品牌整体利润分红")
lines.append("- **门店股东**：仅持有一家门店股份，按该门店利润分红")
lines.append("- 分红计算：分红金额 = 净利润 × 持股比例（自动计算）")
lines.append("- 分红审批：分红方案提交财务审核→总经理批准后执行打款")
lines.append("- 分红记录：历史分红明细查询，到账状态跟踪")
lines.append("")

# 3.6.6 报表体系
lines.append("#### 3.6.6 报表体系")
lines.append("")
lines.append("系统提供的核心财务报表：")
lines.append("")
lines.append("| 报表名称 | 频率 | 内容 | 用户 |")
lines.append("|---------|------|------|------|")
lines.append("| 日结汇总表 | 每日 | 前一日所有已完成订单按门店、业务类型、支付方式分组汇总 | 店长、财务 |")
lines.append("| 月度经营报告 | 每月 | 损益表、收入明细、支出明细、趋势分析 | 店长、财务、总部、投资人 |")
lines.append("| 合并报表（集团） | 每月 | 全部门店汇总利润表、合并收入明细、合并支出明细 | 总部、投资人 |")
lines.append("| 渠道分析报告 | 每月 | 各渠道获客成本、转化率、ROI对比 | 总部运营 |")
lines.append("| 会计凭证 | 每日 | 日结时自动生成的借贷平衡凭证 | 财务 |")
lines.append("| 股东分红报告 | 每月 | 品牌股东和门店股东的分红明细 | 财务、股东 |")
lines.append("")

# ---- D07: 人力资源域 (from V9.3 4.9 人事域) ----
lines.append("### 3.7 人力资源域")
lines.append("")
lines.append("人力资源域覆盖员工信息管理、考勤管理和薪资核算。")
lines.append("")

# 3.7.1 考勤管理
lines.append("#### 3.7.1 考勤管理")
lines.append("")
lines.append("员工通过移动端小程序上下班打卡，系统自动比对排班标记异常。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **移动端打卡**：员工点击“上班打卡”/“下班打卡”，系统记录时间、门店")
lines.append("- **排班管理**：店长预先安排员工每日上下班时间、休息日，支持按周或按月重复")
lines.append("- **迟到/早退/漏卡**：系统自动比对排班标记异常，支持补卡申请（附说明，店长审批）")
lines.append("- **请假审批**：员工申请年假/病假/事假，经店长审批")
lines.append("- **法定假日**：预置国家法定假日，自动识别加班类型")
lines.append("- **月度考勤汇总**：每月最后一日自动生成考勤汇总表（应出勤、实出勤、迟到、早退、加班、请假）")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 请假超过3天需上传医院证明")
lines.append("- 考勤汇总表推送财务作为薪资核算依据")
lines.append("- 加班系数：平日1.5倍，休息日2倍，法定假日3倍")
lines.append("")

# 3.7.2 员工档案
lines.append("#### 3.7.2 员工档案")
lines.append("")
lines.append("总部可创建、编辑、禁用员工账号，关联门店和角色权限。")
lines.append("")
lines.append("**功能点**：")
lines.append("- 创建员工（姓名、手机号、所属门店、岗位、登录密码）")
lines.append("- 员工账号可关联多个门店（跨店调配）")
lines.append("- 员工离职后可禁用账号，保留历史记录")
lines.append("- 角色权限配置（店员/店长/财务/总部等）")
lines.append("")

# 3.7.3 薪资核算
lines.append("#### 3.7.3 薪资核算")
lines.append("")
lines.append("财务每月导入薪资Excel，系统自动计算实发工资并生成人力成本支出记录。")
lines.append("")
lines.append("**流程规则**：")
lines.append("1. 财务导入薪资Excel（模板含员工姓名、门店、基本工资、绩效、社保等）")
lines.append("2. 系统自动计算实发工资 = 应发合计 - 社保（个人）- 个税")
lines.append("3. 生成人力成本支出记录")
lines.append("4. 总部人员薪酬按各店营收占比自动分摊至各门店")
lines.append("5. 支出记录纳入月结报表")
lines.append("")

# ---- D08: 技术域 (from V9.3 4.13 + 4.14) ----
lines.append("### 3.8 技术域")
lines.append("")
lines.append("技术域是ERP系统的技术底座，提供IoT设备管理、智能场景控制、AI经营预警和系统运维支撑。")
lines.append("")

# 3.8.1 IoT设备管理
lines.append("#### 3.8.1 IoT设备管理")
lines.append("")
lines.append("管理各门店的物联网设备，支持设备注册、状态监控、远程控制和故障告警。")
lines.append("")
lines.append("**功能点**：")
lines.append("- **设备注册**：新设备接入时注册至系统（类型、编号、门店、空间位置）")
lines.append("- **状态监控**：实时展示设备在线/离线/故障状态")
lines.append("- **远程控制**：通过智能家居网关下发指令（开门、调温、开关灯等）")
lines.append("- **故障告警**：设备离线超30分钟自动告警，低电量提示")
lines.append("- **设备维保**：记录维修历史、维保计划、到期提醒")
lines.append("")
lines.append("**设备类型**：智能门锁、中央空调（VRF）、灯光照明、电动窗帘、音响/背景音乐")
lines.append("")

# 3.8.2 智能场景联动
lines.append("#### 3.8.2 智能场景联动")
lines.append("")
lines.append("根据客人消费状态自动切换设备组合配置，提供沉浸式空间体验。")
lines.append("")
lines.append("**场景模式**：")
lines.append("")
lines.append("| 场景 | 触发条件 | 灯光 | 空调 | 窗帘 | 音乐 |")
lines.append("|------|---------|------|------|------|------|")
lines.append("| 欢迎 | 预约开始前5分钟 | 迎宾模式（暖黄） | 预冷/预热至26℃ | 打开 | 轻音乐 |")
lines.append("| 品茶 | 客人扫码开门 | 品茶模式（3000K暖光） | 保持26℃ | 半开 | 古筝/轻音乐 |")
lines.append("| 会议 | 店员切换/预约指定 | 会议模式（4000K白光） | 24℃ | 关闭 | 关闭 |")
lines.append("| K歌 | 店员切换/预约指定 | K歌模式（氛围灯） | 24℃ | 关闭 | K歌系统 |")
lines.append("| 节能 | 退房后 | 关闭 | 关闭/设定26℃ | 关闭 | 关闭 |")
lines.append("")
lines.append("**业务规则**：")
lines.append("- 场景切换可在小程序手动操作（客人或店员均可）")
lines.append("- 退房后自动切换为节能模式")
lines.append("- 物理开关/遥控器优先级高于系统指令（设备本地优先）")
lines.append("")

# 3.8.3 AI经营预警
lines.append("#### 3.8.3 AI经营预警")
lines.append("")
lines.append("系统通过数据分析和规则引擎，主动发现经营异常和风险隐患并提供策略建议。")
lines.append("")
lines.append("**预警类型及阈值**：")
lines.append("")
ai_table = """| 预警类型 | 判定条件（默认值） | 推送对象 |
|---------|------------------|---------|
| 营收异常下降 | 当日营收环比下降 ≥ 30%（或连续3日下降 ≥ 15%） | 店长、总部运营 |
| 成本异常上升 | 当月成本率环比上升 ≥ 10%（绝对值） | 店长、财务 |
| 对账大额差异 | 单笔差异金额 > 500元 或 日累计差异 > 1000元 | 店员、店长 |
| 库存积压 | 商品库存周转天数 > 90天 或 临期（< 30天）库存占比 > 20% | 店长、供应链 |
| 设备批量离线 | 单店离线设备数 > 3台 或 同一设备连续离线 > 24小时 | 店员、技术 |
| 客流异常 | 当日客流环比下降 ≥ 40%（排除节假日因素） | 店长、总部运营 |
| 差评预警 | 平台差评数量超过阈值（美团/抖音评分 < 4.5） | 店长、总部运营 |"""
lines.append(ai_table)
lines.append("")
lines.append("**阈值配置说明**：")
lines.append("- 以上阈值均为系统默认值，支持按门店独立配置")
lines.append("- 环比计算周期：默认7天滚动环比，可切换为30天")
lines.append("- 预警频率：同一类型同一门店24小时内仅触发一次")
lines.append("- 预警升级：触发后4小时未被处理，升级推送至上一级管理员")
lines.append("- 静默期：已标记“已处理”的同类型预警，7天内不重复触发")
lines.append("")
lines.append("**预警处理SLA**：")
lines.append("| 预警类型 | 响应时限 | 升级条件 |")
lines.append("|---------|---------|---------|")
lines.append("| 营收异常下降 | 2小时 | 超时→推送至总部运营总监 |")
lines.append("| 成本异常上升 | 4小时 | 超时→推送至财务总监 |")
lines.append("| 对账大额差异 | 1小时 | 超时→推送至财务经理 |")
lines.append("| 库存积压 | 4小时 | 超时→推送至供应链经理 |")
lines.append("| 设备批量离线 | 30分钟 | 超时→推送至技术负责人 |")
lines.append("| 客流异常 | 2小时 | 超时→推送至市场总监 |")
lines.append("| 差评预警 | 1小时 | 超时→推送至运营总监 |")
lines.append("")
lines.append("**AI策略建议**（未来扩展）：")
lines.append("- 定价优化建议（基于客单价和上座率分析）")
lines.append("- 促销时机推荐（基于客流低谷期识别）")
lines.append("- 成本控制建议（基于异常支出检测）")
lines.append("- 会员流失预警与挽回策略")
lines.append("")

# ====================================================================
# APPEND V10.7 TAIL (Ch4 + Ch5 + Appendices)
# ====================================================================
lines.append(tail[ch4_start:])

# ====================================================================
# WRITE OUTPUT
# ====================================================================
output_content = "\n".join(lines)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(output_content)

# Count lines
line_count = output_content.count('\n') + 1
print(f"Reconstructed V10.7: {line_count} lines")
print(f"Output: {OUTPUT}")
print("Done!")
