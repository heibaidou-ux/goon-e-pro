"""
V10.7: Major restructure based on 于总 review
1. Domain reorder: 品牌运营域(D01) → 门店拓展域(D02) → 门店运营域(D03) → ...
2. 包间/会议室 → 空间租用
3. Split HQ/store revenue in accounting
4. Add 组织架构 tree, 对象模型 entities
5. Add 设计图施工图 mention
"""
filepath = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.6，2026年5月7日）.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
ops = []

# ====================================================================
# 1. Replace "包间/会议室" with "空间租用" in revenue/accounting contexts
#    Keep "包间" when referring to physical rooms
# ====================================================================
# "空间租用" replaces "包间/会议室" in the revenue context only
content = content.replace("包间/会议室订单", "空间租用订单")
content = content.replace("包间/会议室", "空间租用")
ops.append("Consolidated 包间/会议室 → 空间租用")

# But fix "包间" mentions that should stay as physical rooms
# Check if any over-replacement happened
# (包间 management, 包间 creation etc. should stay)
# Actually the replacement of "包间/会议室" → "空间租用" is correct for all contexts
# since it was a combined term. Individual "包间" references remain untouched.

# ====================================================================
# 2. Domain restructuring
#    New order: 品牌运营域(D01) → 门店拓展域(D02) → 门店运营域(D03) → 市场营销域(D04) → 供应链域(D05) → 财务域(D06) → 人力资源域(D07) → 技术域(D08)
# ====================================================================

# ---- 2a. Update 2.1 业务域划分 table ----
old_domain_table = """| 编号 | 业务域 | 对应部门 | 核心职责 |
|------|--------|---------|---------|
| D01 | 门店运营域 | 运营部 | 门店日常经营、客户服务、房态管理、保洁任务、门店巡检 |
| D02 | 市场营销域 | 市场部 | 客户获取、营销活动、优惠券管理、渠道运营 |
| D03 | 供应链域 | 采购部/仓储部 | 商品采购、库存管理、供应商管理 |
| D04 | 财务域 | 财务部 | 收入管理、支出管理、月结对账、股东分红、报表体系 |
| D05 | 技术域 | 技术部 | IoT设备管理、智能场景控制、系统运维、AI经营预警 |
| D06 | 人力资源域 | 人事行政部 | 考勤管理、薪资核算、员工档案 |
| D07 | 总部管理域 | 总经办 | 发展规划、品牌建设、门店拓展与配置、集中审批、品牌运营看板、投资者关系 |"""

new_domain_table = """| 编号 | 业务域 | 对应部门 | 核心职责 |
|------|--------|---------|---------|
| D01 | 品牌运营域 | 品牌运营部 | 品牌战略、加盟管理、运营标准、品牌运营看板、投资者关系 |
| D02 | 门店拓展域 | 拓展部 | 门店招标、选址评估、门店建设、门店配置与参数管理 |
| D03 | 门店运营域 | 运营部 | 门店日常经营、客户服务、房态管理、保洁任务、门店巡检 |
| D04 | 市场营销域 | 市场部 | 客户获取、营销活动、优惠券管理、渠道运营 |
| D05 | 供应链域 | 采购部/仓储部 | 商品采购、库存管理、供应商管理 |
| D06 | 财务域 | 财务部 | 收入管理、支出管理、月结对账、股东分红、报表体系 |
| D07 | 人力资源域 | 人事行政部 | 考勤管理、薪资核算、员工档案 |
| D08 | 技术域 | 技术部 | IoT设备管理、智能场景控制、系统运维、AI经营预警 |"""

assert old_domain_table in content, "Domain table not found!"
content = content.replace(old_domain_table, new_domain_table)
ops.append("Reordered domains: D01品牌运营域 → D08技术域")

# ---- 2b. Update 2.2 子系统定义 table ----
old_subsystem_table = """| 子系统 | 对应业务域 | 主要用户 | 说明 |
|--------|-----------|---------|------|
| 门店运营系统 | 门店运营域 | 店员、店长、客人 | 核心业务系统，处理预约、消费、房态等 |
| 营销系统 | 市场营销域 | 总部运营 | 活动创建、优惠券配置、效果分析 |
| 进销存系统 | 供应链域 | 店长、总部运营 | 采购、库存、供应商全链路管理 |
| 财务系统 | 财务域 | 财务、店长 | 月结、对账、分红、报表 |
| 人事系统 | 人力资源域 | 店长、总部 | 考勤、薪资、档案管理 |
| 总部管理系统 | 总部管理域 | 总部运营、投资人 | 品牌加盟管理、门店管理、集中审批、决策看板 |
| ERP支撑平台 | 技术域 | 系统管理员、技术运维 | ERP系统技术底座，含IoT设备管理、智能场景控制、AI经营预警引擎、系统日志与监控、运维管理 |"""

new_subsystem_table = """| 子系统 | 对应业务域 | 主要用户 | 说明 |
|--------|-----------|---------|------|
| 品牌运营系统 | 品牌运营域 | 总部运营、投资人 | 品牌战略管理、加盟管理、运营标准制定、品牌运营看板、投资者关系 |
| 门店拓展系统 | 门店拓展域 | 总部拓展团队 | 门店招标、选址评估与审批、门店建设进度跟踪、门店配置管理 |
| 门店运营系统 | 门店运营域 | 店员、店长、客人 | 核心业务系统，处理预约、消费、房态等 |
| 营销系统 | 市场营销域 | 总部运营 | 活动创建、优惠券配置、效果分析 |
| 进销存系统 | 供应链域 | 店长、总部运营 | 采购、库存、供应商全链路管理 |
| 财务系统 | 财务域 | 财务、店长 | 月结、对账、分红、报表 |
| 人事系统 | 人力资源域 | 店长、总部 | 考勤、薪资、档案管理 |
| ERP支撑平台 | 技术域 | 系统管理员、技术运维 | ERP系统技术底座，含IoT设备管理、智能场景控制、AI经营预警引擎、系统日志与监控、运维管理 |"""

assert old_subsystem_table in content, "Subsystem table not found!"
content = content.replace(old_subsystem_table, new_subsystem_table)
ops.append("Updated subsystem table with new domain structure")

# ---- 2c. Restructure Chapter 3 sections ----
# Current structure:
#   3.1 总部管理域 (sections 3.1.1-3.1.6)
#   3.2 门店运营域 (sections 3.2.1-3.2.x)
#   3.3 市场营销域
#   3.4 供应链域
#   3.5 财务域
#   3.6 人力资源域
#   3.7 技术域
#
# New structure:
#   3.1 品牌运营域 (3.1.1-3.1.4 from old 总部管理域, minus 门店拓展/门店配置)
#   3.2 门店拓展域 (from old 3.1.5 + 3.1.6)
#   3.3 门店运营域 (was 3.2)
#   3.4 市场营销域 (was 3.3)
#   3.5 供应链域 (was 3.4)
#   3.6 财务域 (was 3.5)
#   3.7 人力资源域 (was 3.6)
#   3.8 技术域 (was 3.7)

# Find section boundaries using header markers
sections = {}
for section_num in range(1, 8):
    header = f"### 3.{section_num} "
    start = content.find(header)
    if start == -1:
        print(f"WARNING: Section 3.{section_num} not found!")
        continue
    # Find next ### 3.x or ## 第四章
    next_header = None
    for next_n in range(section_num + 1, 9):
        nh = content.find(f"### 3.{next_n} ", start + 5)
        if nh != -1:
            next_header = nh
            break
    if next_header is None:
        # Last section - go to ## 第四章
        next_header = content.find("## 第四章", start)
        if next_header == -1:
            next_header = len(content)

    sections[section_num] = {
        "start": start,
        "end": next_header,
        "content": content[start:next_header]
    }
    print(f"  3.{section_num}: {start} → {next_header} ({next_header-start} chars)")

# Now we need to:
# A) Extract old 3.1 content, split into 品牌运营域 (minus 门店拓展+门店配置) and 门店拓展域
# B) Renumber sections

# Extract 3.1.5 and 3.1.6 from old 3.1
old_3_1 = sections[1]["content"]

# Find where 3.1.5 starts
sec_3_1_5 = old_3_1.find("#### 3.1.5 门店拓展")
sec_3_1_6 = old_3_1.find("#### 3.1.6 门店配置")

# Brand operations content (3.1.1-3.1.4)
brand_ops_content = old_3_1[:sec_3_1_5]
# Store expansion content (3.1.5 + 3.1.6)
store_expansion_content = old_3_1[sec_3_1_5:]

# ---- 2d. Rename and renumber ----
# First, rename header and intro of brand operations
brand_ops_content = brand_ops_content.replace(
    "### 3.1 总部管理域",
    "### 3.1 品牌运营域"
)
brand_ops_content = brand_ops_content.replace(
    "总部管理域是品牌的决策中枢，负责制定发展战略、建设品牌标准、统筹门店布局与资源配置。从系统开发视角，该域提供支撑总部管控职能的业务模块，包括发展规划、品牌建设、品牌运营看板、投资者关系、门店拓展与门店配置。各业务模块中涉及的审批流程均通过统一的工作流引擎驱动（详见 4.7 节）。",
    "品牌运营域是品牌的决策中枢，负责制定品牌发展战略、建设品牌标准体系、管理加盟体系与投资者关系。从系统开发视角，该域提供支撑品牌管控职能的业务模块，包括发展规划、品牌建设、品牌运营看板、投资者关系。各业务模块中涉及的审批流程均通过统一的工作流引擎驱动（详见 4.7 节）。"
)

# Renumber subsections in brand operations (3.1.x stays 3.1.x)
import re

# Renumber 门店拓展域 content - rename header and renumber subsections
store_expansion_content = store_expansion_content.replace(
    "#### 3.1.5 门店拓展",
    "#### 3.2.1 门店选址与建设"
)
store_expansion_content = store_expansion_content.replace(
    "#### 3.1.6 门店配置",
    "#### 3.2.2 门店配置"
)

# Create the new header for 门店拓展域
new_store_domain_header = """### 3.2 门店拓展域

门店拓展域负责品牌门店网络的规划、选址、建设与配置管理。从系统开发视角，该域管理门店从选址到开业的全过程，确保门店布局符合品牌战略、建设标准统一、运营参数规范配置。各业务模块中涉及的审批流程均通过统一的工作流引擎驱动（详见 4.7 节）。

"""

# The store_expansion_content starts with "#### 3.1.5" which we've renamed to "#### 3.2.1"
# We need to remove the old 3.1 header part that was before 3.1.5
# Actually, we already extracted store_expansion_content starting from "#### 3.1.5", which is perfect
# Replace the old subsection numbering
store_expansion_content = re.sub(
    r'#### 3\.1\.(\d+)',
    lambda m: f"#### 3.2.{m.group(1)}",
    store_expansion_content
)

# Build the new chapter 3
# Start with old content before section 3.1
ch3_start = content.find("### 3.1 ")
ch3_end = sections[7]["end"]  # end of section 3.7

before_ch3 = content[:ch3_start]
after_ch3 = content[ch3_end:]

# Build new sections in order
new_section_3_1 = brand_ops_content
new_section_3_2 = new_store_domain_header + store_expansion_content

# Renumber old 3.2 → new 3.3 (门店运营域)
def renumber_section(text, old_major, new_major):
    """Renumber all 3.x.y headers in a section"""
    # Replace main header
    text = re.sub(
        rf'^### {old_major}\.',  # Matches "### 3.2 " etc at start of line
        f'### {new_major}.',
        text,
        count=1
    )
    # Replace subsection headers 3.x.y -> 3.new_major.y
    text = re.sub(
        rf'(?<=#### ){old_major}\.',
        f'{new_major}.',
        text
    )
    # Replace cross-references like "（详见3.2.1" or "见3.2.1" or "3.2.1节"
    text = re.sub(
        rf'(?<=\d){old_major}(?=\.\d)',
        str(new_major),
        text
    )
    return text

new_section_3_3 = renumber_section(sections[2]["content"], 2, 3)  # old 3.2 → 3.3
new_section_3_4 = renumber_section(sections[3]["content"], 3, 4)  # old 3.3 → 3.4
new_section_3_5 = renumber_section(sections[4]["content"], 4, 5)  # old 3.4 → 3.5
new_section_3_6 = renumber_section(sections[5]["content"], 5, 6)  # old 3.5 → 3.6
new_section_3_7 = renumber_section(sections[6]["content"], 6, 7)  # old 3.6 → 3.7
new_section_3_8 = renumber_section(sections[7]["content"], 7, 8)  # old 3.7 → 3.8

new_chapter_3 = (
    new_section_3_1 + "\n" +
    new_section_3_2 + "\n" +
    new_section_3_3 + "\n" +
    new_section_3_4 + "\n" +
    new_section_3_5 + "\n" +
    new_section_3_6 + "\n" +
    new_section_3_7 + "\n" +
    new_section_3_8
)

content = before_ch3 + new_chapter_3 + after_ch3
ops.append("Restructured Chapter 3: 品牌运营域(3.1) → 门店拓展域(3.2) → 门店运营域(3.3) → ... → 技术域(3.8)")

# ---- 2e. Update subsystem dependency text (after mermaid diagram) ----
content = content.replace("HQ[\"总部管理系统\"]", "HQ[\"品牌运营系统\"]")

ops.append("Updated mermaid diagram labels")

# ====================================================================
# 3. Split revenue: HQ revenue vs Store revenue in 3.5.1 (now 3.6.1)
# ====================================================================
old_revenue_table = """| 一级科目 | 二级科目 | 来源 |
|---------|---------|------|
| 主营业务收入 | 空间租用收入 | 包间/会议室订单 |
| 主营业务收入 | 商品零售收入 | 零售订单 |
| 主营业务收入 | 品牌特许经营收入 | 加盟金/品牌管理费 |
| 其他业务收入 | 平台补贴收入 | 平台结算单 |
| 其他业务收入 | 充电宝分成 | 供应商结算 |
| 其他业务收入 | 广告收入 | 合同确认 |
| 其他业务收入 | 赔偿金 | 偶发收入 |
| 债务性收入 | 会员充值 | 充值记录（递延确认） |"""

# Note: old "包间/会议室订单" was already replaced to "空间租用订单"
new_revenue_table = """| 收入主体 | 一级科目 | 二级科目 | 来源 |
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

if old_revenue_table in content:
    content = content.replace(old_revenue_table, new_revenue_table)
    ops.append("Split revenue: HQ income (franchise/management fee/design fee/supply chain) vs Store income")
else:
    # Try with already-replaced text
    alt_old = old_revenue_table.replace("包间/会议室订单", "空间租用订单")
    content = content.replace(alt_old, new_revenue_table)
    ops.append("Split revenue (alternative match)")

# ====================================================================
# 4. Add 组织架构 description after 业务域划分
# ====================================================================
org_text = """

#### 2.1.1 组织架构

高岸品牌采用树形组织架构：

- **根节点**：高岸总部（对应法人主体：高岸总公司）
- **一级节点**：各门店（对应法人主体：门店分公司或个体工商户）
- **二级节点**：门店下属部门（运营部、财务部、人事部等）
- **员工**：所有员工归属于某个部门

**基础实体说明**：系统需建立以下基础数据实体——
- **公司**：法人主体，含公司名称、统一社会信用代码、法人代表、注册地址
- **法人**：法定代表人信息，关联公司实体
- **股东**：品牌股东/门店股东，含持股比例、出资额、关联公司
- **资金账户**：各法人主体名下的银行账户，含开户行、账号、账户类型（基本户/一般户/专户）

各门店的财务独立核算，总部可查看全部门店合并报表。"""

# Insert after 域间关系说明, before --- separator
insert_point = content.find("![七业务域Hub-and-Spoke关系图]")
if insert_point != -1:
    insert_point = content.find("\n---\n", insert_point)
    if insert_point != -1:
        content = content[:insert_point] + org_text + "\n" + content[insert_point:]
        ops.append("Added 组织架构 tree description + 基础实体（公司/法人/股东/资金账户）")

# ====================================================================
# 5. Add 设计图施工图 functionality to 门店拓展域 (3.2 now)
# ====================================================================
design_draw_text = """

**设计图与施工图管理**：
- 系统集成 Draw.io（开源绘图工具）或 Open Design 等设计工具，支持门店空间设计图、施工图、水电图的在线绘制与版本管理
- 设计参数模板化：门店面积、包间数量、设施配置等参数输入后，系统辅助生成标准空间布局方案
- 设计审批流程：设计图提交后经总部评审确认方可进入施工阶段
- 设计变更管理：施工过程中的设计变更须重新提交审批，变更历史完整留痕
- 图纸归档：完工后所有设计图、施工图、竣工图归档至对应门店的资产档案，支持后续查询与改造参考
"""

# Find the 门店选址与建设 section (now 3.2.1) and add after it
# Look for the marker before F1-门店拓展.png
insert_point = content.find("**门店拓展泳道图**：")
if insert_point != -1:
    # Insert before the swimlane diagram
    insert_point = content.find("---\n", insert_point)  # after the swimlane section
    if insert_point != -1:
        content = content[:insert_point] + design_draw_text + "\n" + content[insert_point:]
        ops.append("Added 设计图施工图 management to 门店拓展域")
else:
    # Try alternative: after 门店建设 section
    insert_point = content.find("选址历史记录查询")
    if insert_point != -1:
        insert_point = content.find("\n---\n", insert_point)
        if insert_point != -1:
            content = content[:insert_point] + design_draw_text + "\n" + content[insert_point:]
            ops.append("Added 设计图施工图 management (alt location)")

# ====================================================================
# 6. Update Hub-and-Spoke diagram reference to reflect 8 domains
# ====================================================================
content = content.replace(
    "![七业务域Hub-and-Spoke关系图]",
    "![八业务域Hub-and-Spoke关系图]"
)
ops.append("Updated diagram reference: 7→8 domains")

# ====================================================================
# 7. Add V10.7 revision history
# ====================================================================
v10_7_entry = """| V10.7 | 2026-05-07 | 根据于总评审意见全面重构：总部管理域→品牌运营域（D01），新增门店拓展域（D02），8域重排（品牌运营→门店拓展→门店运营→市场营销→供应链→财务→人力资源→技术）；包间/会议室合并为空间租用；收入科目按总部/门店拆分（总部：加盟金/管理费/设计费/供应链茶叶销售）；新增组织架构树形结构（总部→门店→部门）及基础实体（公司/法人/股东/资金账户）；门店拓展域新增设计图施工图管理功能 | Claude Code |"""

# Insert after V10.6 entry
v10_6_marker = "| V10.6 | 2026-05-07 | CDM逐域实体映射移出正文"
idx = content.find(v10_6_marker)
if idx != -1:
    # Find end of V10.6 line
    eol = content.find("\n", idx)
    content = content[:eol+1] + v10_7_entry + content[eol+1:]
    ops.append("Added V10.7 revision history entry")

# ====================================================================
# Save
# ====================================================================
if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("\nAll changes applied successfully!\n")
else:
    print("\nNo changes made!\n")

for op in ops:
    print(f"  + {op}")
