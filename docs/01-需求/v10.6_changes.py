"""
Apply V10.6 changes:
1. Compress CDM section (remove 2.5.3 detailed mapping, keep summary)
2. Incorporate Claude V7.0's income channel mapping style
"""
filepath = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.0，2026年5月6日）.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
ops = []

# ====================================================================
# 1. Compress CDM: Keep 2.5.2 summary, remove 2.5.3 detailed mapping
# ====================================================================

# Find the start and end of 2.5.3
sec_start = content.find("#### 2.5.3 逐域实体映射")
if sec_start != -1:
    # Find the next ## after 2.5.3 (should be "## 第三章")
    next_chapter = content.find("## 第三章", sec_start)
    if next_chapter != -1:
        # The 2.5.3 section ends at the --- before ## 第三章
        sec_end = content.rfind("---", sec_start, next_chapter)
        if sec_end != -1:
            # Replace entire 2.5.3 with a brief note
            replacement = (
                "#### 2.5.3 逐域实体映射\n\n"
                "各业务域与 CDM 实体的详细逐域映射（含 7 大域共 69 个实体的精确映射/近似映射/概念映射标注）"
                "已整理至独立文档《高岸ERP系统-CDMA实体映射说明书》，本文档不再逐表罗列。\n\n"
                "以下仅以域间总览呈现各域的 CDM 覆盖情况：\n\n"
            )
            # But we want to keep the summary table (2.5.2) which is BEFORE 2.5.3
            # So just replace from sec_start to sec_end
            content = content[:sec_start] + replacement + content[sec_end:]
            ops.append("Compressed CDM 2.5.3: removed detailed mapping tables, kept summary reference")
        else:
            print("WARNING: Could not find end of 2.5.3")
    else:
        print("WARNING: Could not find 第三章")
else:
    print("WARNING: Could not find 2.5.3")

# ====================================================================
# 2. Incorporate Claude V7.0's income channel mapping style
#    Replace the "对账明细字段对照表" with a cleaner "收入渠道对账口径" table
# ====================================================================

# Find the field mapping table we added earlier and replace it
old_table_header = "**对账明细字段对照表**"
if old_table_header in content:
    # Find the table header and the table content
    table_start = content.find(old_table_header)
    table_header_end = content.find("\n", table_start)

    # Find the end of this section (next double-newline that's a section break)
    # The table goes from this header to either "**阈值配置说明**" or the next ---
    # Actually, the field mapping table is followed by "月结时以各平台结算单汇总金额..."
    # Let's find that
    end_marker = "月结时以各平台结算单汇总金额与系统收入流水进行汇总比对"
    end_pos = content.find(end_marker, table_start)
    if end_pos != -1:
        end_pos += len(end_marker)
        end_pos = content.find("\n", end_pos)  # go to end of that line
        if end_pos == -1:
            end_pos = content.find("\n\n", table_start)

        # New income channel mapping in Claude's style
        new_mapping = """**收入渠道对账口径**：

| 收入渠道 | 对账口径 | 查询路径 |
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
| 平台补贴收入 | 按平台结算单确认 | 各平台结算中心 |

**对账说明**：
- 美团"茶室"类目与"CAFE"类目的结算科目不同，茶室类目按"房间费+商品费"合并结算，CAFE类目按单品结算
- 抖音结算单含订单金额、平台佣金、达人佣金、平台补贴四项，需分别入账
- 各平台均为T+1结算周期（美团结算周期为14天自动/可手工提现）
- 月结时以各平台结算单汇总金额与系统收入流水进行汇总比对（总额对账），确保账实一致
"""
        # Replace from old table header to end of its section
        content = content[:table_start] + new_mapping + content[end_pos:]
        ops.append("Replaced field mapping table with cleaner income channel mapping (Claude style)")
    else:
        print("WARNING: Could not find end of old field mapping table")
else:
    print("WARNING: Could not find old field mapping table header")

# ====================================================================
# Update version references in filename later
# ====================================================================

if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("\nAll changes applied successfully!\n")
else:
    print("\nNo changes made!\n")

for op in ops:
    print(f"  + {op}")
