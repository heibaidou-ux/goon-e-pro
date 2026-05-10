"""Fix quoting issues in reconstruct_v10.7.py"""
filepath = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\docs\01-需求\reconstruct_v10.7.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = []
for i, line in enumerate(lines):
    # Check if this is lines.append("...") with inner quotes
    stripped = line.rstrip()
    if stripped.startswith('lines.append("') and stripped.endswith('")'):
        # Count quotes between the first and last
        inner = stripped[14:-2]  # content between lines.append(" and ")
        if '"' in inner:
            # Replace inner quotes with Chinese quotes
            # First " after lines.append( is the opening
            # Replace alternating inner "s with “ and ”
            new_inner = []
            toggle = True
            for c in inner:
                if c == '"':
                    new_inner.append('“' if toggle else '”')
                    toggle = not toggle
                else:
                    new_inner.append(c)
            stripped = 'lines.append("' + ''.join(new_inner) + '")'
            print(f"Line {i+1}: fixed {inner.count(chr(34))} quotes")
    fixed.append(stripped)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed) + '\n')

print("Done!")
