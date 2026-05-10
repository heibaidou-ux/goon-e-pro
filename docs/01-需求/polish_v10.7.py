"""Post-process V10.7 MD: fix duplicates, add swimlane images, polish content."""
import sys

filepath = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.7，2026年5月7日）.md'
IMAGES = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\02-设计\images'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
ops = []

# ====================================================================
# 1. Fix duplicate lines
# ====================================================================

# Remove duplicate "所有其他功能" lines (appears on consecutive lines)
import re
content = re.sub(r'(所有其他功能[^。]+。)\n\1', r'\1', content)
ops.append("Removed duplicate line")

# Remove duplicate "### 1.1 项目背景"
content = content.replace("### 1.1 项目背景\n\n### 1.1 项目背景", "### 1.1 项目背景")
ops.append("Fixed duplicate 1.1 header")

# ====================================================================
# 2. Add swimlane images before section end markers
# ====================================================================

swimlane_images = [
    # (insert_after_text, image_name, section_desc)
    ("门店选址与建设", "F1-门店拓展.png", "门店拓展泳道图"),
    ("门店创建与信息维护", "F2-门店配置.png", "门店配置泳道图"),
    ("同一时段同一空间不可重复预约", "F01-包间预约到店消费.png", "包间预约到店消费泳道图"),
    ("超过48小时未取自动退款", "F02-商品零售与外卖.png", "商品零售与外卖泳道图"),
    ("清洁中发现设备故障", "F03-保洁任务与超时升级.png", "保洁任务与超时泳道图"),
    ("自动告警总部", "F04-门店巡检与整改.png", "门店巡检与整改泳道图"),
    ("严禁在平台侧直接修改价格", "F05-营销活动创建审批发布.png", "营销活动创建审批发布泳道图"),
    ("退单时优惠券按规则退回", "F06-优惠券发放与核销.png", "优惠券发放与核销泳道图"),
    ("退货并重新采购", "F07-采购审批入库.png", "采购审批入库泳道图"),
    ("到期商品系统自动锁定不可销售", "F08-库存盘点.png", "库存盘点泳道图"),
    ("不纳入双方门店可用库存", "F09-库存调拨.png", "库存调拨泳道图"),
    ("请款申请（事前）", "F10-请款审批.png", "请款审批泳道图"),
    ("薪资导入", "F11-报销审批.png", "报销审批泳道图"),
    ("推送报告至相关方", "F12-自动月结.png", "自动月结泳道图"),
    ("日结时自动生成的借贷平衡凭证", "F15-日结与凭证.png", "日结与凭证泳道图"),
    ("ERP内部异常", "F13-平台对账差异.png", "平台对账差异泳道图"),
    ("历史分红明细查询，到账状态跟踪", "F14-股东分红.png", "股东分红泳道图"),
    ("加班系数", "F19-考勤与请假.png", "考勤与请假泳道图"),
    ("设备维保", "F18-IoT设备故障.png", "IoT设备故障泳道图"),
    ("物理开关/遥控器优先级高于系统指令", "F16-智能场景联动.png", "智能场景联动泳道图"),
    ("会员流失预警与挽回策略", "F17-AI预警.png", "AI预警泳道图"),
]

for after_text, img_name, desc in swimlane_images:
    insert_marker = f"**{desc}**："
    if img_name in content:
        continue  # already present

    # Find the anchor text to insert after
    pos = content.find(after_text)
    if pos == -1:
        # Try the insert marker directly
        if insert_marker in content:
            continue  # already has formatted swimlane reference

        # Try to find an alternative insertion point
        # Look near the end of the relevant section
        print(f"  WARNING: Could not find anchor for {img_name} (after: {after_text[:30]})")
        continue

    # Find the end of the paragraph containing after_text
    # Go to the next double newline or next ### header
    para_end = content.find("\n\n", pos)
    if para_end == -1:
        para_end = content.find("\n### ", pos)
    if para_end == -1:
        para_end = pos + len(after_text) + 50

    # Insert the swimlane image after the paragraph end
    img_ref = f"\n\n**泳道图**：\n\n![](../02-设计/images/{img_name})"

    # Check if we already have a swimlane-like reference
    next_100 = content[para_end:para_end+100]
    if "泳道图" in next_100:
        # Another swimlane is nearby — insert this one AFTER it
        swimlane_match = re.search(r'!\[\]\(\.\./02-设计/images/.*?\.png\)', content[para_end:para_end+200])
        if swimlane_match:
            insert_at = para_end + swimlane_match.end()
            content = content[:insert_at] + img_ref + content[insert_at:]
            ops.append(f"Added {img_name}")
        continue

    content = content[:para_end] + img_ref + content[para_end:]
    ops.append(f"Added {img_name}")

# ====================================================================
# 3. Fix V10.x-specific: ensure cross-references to sections are correct
# ====================================================================

# Update old section references
content = content.replace("（详见 4.7 节）", "（详见 4.7 节工作流引擎要求）")
content = content.replace("（详见 4.7 节工作流引擎要求工作流引擎要求）", "（详见 4.7 节工作流引擎要求）")

# ====================================================================
# Save
# ====================================================================
if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Applied {len(ops)} changes:")
    for op in ops:
        print(f"  + {op}")
else:
    print("No changes applied!")

# Count lines
print(f"\nTotal lines: {content.count(chr(10)) + 1}")
