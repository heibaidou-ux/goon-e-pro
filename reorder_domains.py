filepath = r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\高岸ERP系统-需求说明书（V10.0，2026年5月6日）.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
ops = []

# ================================================================
# Reorder 2.5.3 subsections: HQ first, Tech last
# New order: D07总部 → D01门店运营 → D02市场营销 → D03供应链 → D04财务 → D06人力资源 → D05技术
# ================================================================

# The 2.5.3 section contains 7 subsections: ##### D01 through ##### D07
# Each subsection runs from its ##### header to the next ##### or --- separator before "## 第三章"

# Find the start of 2.5.3
section_start = content.find("#### 2.5.3 逐域实体映射")
assert section_start != -1, "2.5.3 section not found!"

# Find the first ##### D01 after 2.5.3
d01_pos = content.find("##### D01", section_start)
d02_pos = content.find("##### D02", section_start)
d03_pos = content.find("##### D03", section_start)
d04_pos = content.find("##### D04", section_start)
d05_pos = content.find("##### D05", section_start)
d06_pos = content.find("##### D06", section_start)
d07_pos = content.find("##### D07", section_start)

# The section ends with "---\n\n## 第三章"
chapter3_pos = content.find("## 第三章：功能需求", section_start)
# Go back to find the --- before chapter 3
end_pos = content.rfind("---", section_start, chapter3_pos)
# end_pos should be the --- line before ## 第三章

print(f"D01 at {d01_pos}, D02 at {d02_pos}, D03 at {d03_pos}, D04 at {d04_pos}, D05 at {d05_pos}, D06 at {d06_pos}, D07 at {d07_pos}")
print(f"end_pos = {end_pos}, chapter3_pos = {chapter3_pos}")

# Extract each subsection
sections = {}
for label, pos_start in [("D01", d01_pos), ("D02", d02_pos), ("D03", d03_pos), ("D04", d04_pos), ("D05", d05_pos), ("D06", d06_pos), ("D07", d07_pos)]:
    # Find next ##### or end
    next_start = None
    for next_label in ["D01", "D02", "D03", "D04", "D05", "D06", "D07"]:
        p = content.find(f"##### {next_label}", pos_start + 10)
        if p != -1 and p != pos_start:
            if next_start is None or p < next_start:
                next_start = p

    if next_start is None:
        # Last section - end at --- before chapter 3
        section_end = end_pos
    else:
        section_end = next_start

    sections[label] = content[pos_start:section_end]
    print(f"  {label}: from {pos_start} to {section_end} ({section_end - pos_start} chars)")

# New order: D07总部 → D01门店运营 → D02市场营销 → D03供应链 → D04财务 → D06人力资源 → D05技术
# Renumber: D01=总部, D02=门店运营, D03=市场营销, D04=供应链, D05=财务, D06=人力资源, D07=技术
old_to_new_number = {
    "D07": "D01",  # 总部管理域 → D01
    "D01": "D02",  # 门店运营域 → D02
    "D02": "D03",  # 市场营销域 → D03
    "D03": "D04",  # 供应链域 → D04
    "D04": "D05",  # 财务域 → D05
    "D06": "D06",  # 人力资源域 → D06
    "D05": "D07",  # 技术域 → D07
}

old_domain_names = {
    "D01": "门店运营域",
    "D02": "市场营销域",
    "D03": "供应链域",
    "D04": "财务域",
    "D05": "技术域",
    "D06": "人力资源域",
    "D07": "总部管理域",
}

new_domain_names = {
    "D01": "总部管理域",
    "D02": "门店运营域",
    "D03": "市场营销域",
    "D04": "供应链域",
    "D05": "财务域",
    "D06": "人力资源域",
    "D07": "技术域",
}

# Replace old numbers with new numbers in each section, and replace domain names
def renumber_section(text, old_label, new_label):
    old_number = old_label  # e.g., "D01"
    new_number = new_label  # e.g., "D02"
    old_name = old_domain_names[old_label]
    new_name = new_domain_names[new_label]

    text = text.replace(f"##### {old_number} {old_name}", f"##### {new_number} {new_name}")
    return text

# Build new order in the new numbering
new_order = ["D07", "D01", "D02", "D03", "D04", "D06", "D05"]
# new_order uses OLD labels (the keys of our dictionaries)
# We want:
# 1st: D07 总部管理域 → becomes D01 总部管理域
# 2nd: D01 门店运营域 → becomes D02 门店运营域
# 3rd: D02 市场营销域 → becomes D03 市场营销域
# 4th: D03 供应链域   → becomes D04 供应链域
# 5th: D04 财务域     → becomes D05 财务域
# 6th: D06 人力资源域 → becomes D06 人力资源域 (same number!)
# 7th: D05 技术域     → becomes D07 技术域

reordered_content = ""
for old_label in new_order:
    new_label = old_to_new_number[old_label]
    renamed = renumber_section(sections[old_label], old_label, new_label)
    reordered_content += renamed

print("\nNew order sections:")
for old_label in new_order:
    new_label = old_to_new_number[old_label]
    name = new_domain_names[new_label]
    print(f"  {new_label} {name} (was {old_label})")

# Verify the reordered content has no old labels
for old_label, new_label in old_to_new_number.items():
    if old_label != new_label:
        # Check old labels don't appear as D0X headers
        old_name = old_domain_names[old_label]
        assert f"##### {old_label} {old_name}" not in reordered_content, f"Old label {old_label} still found!"

print("All old labels successfully replaced!")

# Now replace the original section block
# Extract the old block: from first ##### D01 to end_pos
old_block = content[d01_pos:end_pos]

# Replace with reordered content
content = content[:d01_pos] + reordered_content + content[end_pos:]

ops.append("Reordered 2.5.3 subsections: D07总部→D01, D05技术→D07")

# ================================================================
# Update 2.5.2 summary table
# ================================================================
old_table = """| 高岸业务域 | 主要CDM实体组 | 实体数量（映射） | 匹配程度 |
|-----------|--------------|----------------|---------|
| D01 门店运营域 | applicationCommon（Account/Contact/Order/Appointment/Service/Task） | 12 | 精确映射为主 |
| D02 市场营销域 | applicationCommon（Campaign/Lead/Opportunity/MarketingList/Segment）+ 客户标签 | 9 | 精确映射为主 |
| D03 供应链域 | foundationCommon + operationsCommon（Product/PurchaseOrder/Vendor/Inventory/Warehouse）+ 批次/有效期 | 13 | 精确映射为主 |
| D04 财务域 | operationsCommon（MainAccount/Ledger/Budget/Invoice/Payment/FiscalCalendar）+ GL凭证/AP | 14 | 精确映射为主 |
| D05 技术域 | applicationCommon（Device/SystemJob/AuditLog）+ 自定义扩展 | 5 | 概念映射+扩展 |
| D06 人力资源域 | operationsCommon（Employee/Job/Position/Payroll/Compensation） | 8 | 精确映射为主 |
| D07 总部管理域 | applicationCommon（Organization/BusinessUnit/Goal/GoalMetric/Territory） | 8 | 近似映射为主 |"""

new_table = """| 高岸业务域 | 主要CDM实体组 | 实体数量（映射） | 匹配程度 |
|-----------|--------------|----------------|---------|
| D01 总部管理域 | applicationCommon（Organization/BusinessUnit/Goal/GoalMetric/Territory） | 8 | 近似映射为主 |
| D02 门店运营域 | applicationCommon（Account/Contact/Order/Appointment/Service/Task） | 12 | 精确映射为主 |
| D03 市场营销域 | applicationCommon（Campaign/Lead/Opportunity/MarketingList/Segment）+ 客户标签 | 9 | 精确映射为主 |
| D04 供应链域 | foundationCommon + operationsCommon（Product/PurchaseOrder/Vendor/Inventory/Warehouse）+ 批次/有效期 | 13 | 精确映射为主 |
| D05 财务域 | operationsCommon（MainAccount/Ledger/Budget/Invoice/Payment/FiscalCalendar）+ GL凭证/AP | 14 | 精确映射为主 |
| D06 人力资源域 | operationsCommon（Employee/Job/Position/Payroll/Compensation） | 8 | 精确映射为主 |
| D07 技术域 | applicationCommon（Device/SystemJob/AuditLog）+ 自定义扩展 | 5 | 概念映射+扩展 |"""

assert old_table in content, "Old 2.5.2 table not found!"
content = content.replace(old_table, new_table)
ops.append("Updated 2.5.2 summary table with new numbering")

# ================================================================
# Save
# ================================================================
if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("\nAll changes applied successfully!\n")
else:
    print("\nNo changes made!\n")

for op in ops:
    print(f"  + {op}")

# Quick verification
print("\n--- Verification ---")
for idx, old_label in enumerate(new_order):
    new_label = old_to_new_number[old_label]
    name = new_domain_names[new_label]
    check = f"##### {new_label} {name}"
    found = check in content
    print(f"  {check}: {'OK' if found else 'MISSING!'}")
