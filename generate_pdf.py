"""
Generate PDF: MD → HTML (mermaid pre-rendered via mmdc, images base64) → Chrome print-to-pdf
"""
import re, os, subprocess, base64, shutil, json, sys
from pathlib import Path

BASE = Path(r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP")
MMDC = r"C:\Users\王晓东\AppData\Roaming\npm\mmdc.cmd"
MD_FILE = BASE / "docs" / "01-需求" / "高岸ERP系统-需求说明书（V10.8，2026年5月8日）.md"
IMAGES_DIR = BASE / "docs" / "02-设计" / "images"
OUTPUT_DIR = BASE / "docs" / "01-需求"
WORK_DIR = BASE / "tmp_pdf_build"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
WORK_DIR.mkdir(parents=True)

with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_content = f.read()

print("Step 1: Pre-rendering Mermaid diagrams via mmdc...")

# Create puppeteer config for mmdc to use local Chrome
puppeteer_config = WORK_DIR / "puppeteer-config.json"
with open(puppeteer_config, 'w', encoding='utf-8') as f:
    json.dump({
        "executablePath": CHROME,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"]
    }, f)

def render_mermaid_via_mmdc(mermaid_code, index):
    """Render mermaid to PNG using mmdc with local Chrome."""
    mmd_file = WORK_DIR / f"diagram_{index}.mmd"
    png_file = WORK_DIR / f"mermaid_{index}.png"

    with open(mmd_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_code.strip())

    result = subprocess.run([
        MMDC,
        "-i", str(mmd_file),
        "-o", str(png_file),
        "-p", str(puppeteer_config),
        "-b", "white",
        "-s", "3"
    ], capture_output=True, timeout=60)

    if png_file.exists() and png_file.stat().st_size > 100:
        return png_file
    else:
        print(f"  STDERR: {result.stderr.decode('utf-8', errors='replace')[:300]}")
        return None

mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', md_content, re.DOTALL)
print(f"  Found {len(mermaid_blocks)} mermaid blocks")

for i, block in enumerate(mermaid_blocks):
    print(f"  Rendering diagram {i+1}/{len(mermaid_blocks)}...", end=" ")
    sys.stdout.flush()
    png_path = render_mermaid_via_mmdc(block.strip(), i + 1)
    if png_path:
        b64 = base64.b64encode(open(png_path, 'rb').read()).decode()
        old = f"```mermaid\n{block}```"
        new = f"![mermaid-diagram](data:image/png;base64,{b64})"
        md_content = md_content.replace(old, new, 1)
        print(f"OK ({png_path.stat().st_size//1024}KB)")
    else:
        print("FAILED (leaving as text)")

print("Step 2: Embedding swimlane images as base64...")
img_count = 0
for img_file in sorted(IMAGES_DIR.iterdir()):
    if not img_file.is_file():
        continue
    rel_path = f"../02-设计/images/{img_file.name}"
    if rel_path not in md_content:
        print(f"  SKIP: {img_file.name} not referenced in MD")
        continue
    b64 = base64.b64encode(img_file.read_bytes()).decode()
    md_content = md_content.replace(rel_path, f"data:image/png;base64,{b64}")
    img_count += 1
    print(f"  Embedded: {img_file.name}")

print(f"  Done: {img_count} images embedded")

print("Step 3: Converting MD to HTML...")
from markdown_it import MarkdownIt
md_parser = MarkdownIt('default', {'breaks': True, 'html': True})
html_body = md_parser.render(md_content)

print("Step 3a: Generating table of contents...")
import html as html_mod

def generate_toc(html_body):
    """Build a table of contents from HTML headers, with anchor links."""
    # Find all h1/h2/h3 tags, extract their text
    toc_items = []
    seen = {}
    for m in re.finditer(r'<h([1-3])(\s+[^>]*)?>(.*?)</h\1>', html_body, re.IGNORECASE):
        level = int(m.group(1))
        text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        if not text:
            continue
        # Generate anchor id from text
        anchor_id = re.sub(r'[^\w一-鿿_-]', '', text)[:40]
        if not anchor_id:
            anchor_id = f"h{len(toc_items)}"
        # Deduplicate
        if anchor_id in seen:
            seen[anchor_id] += 1
            anchor_id = f"{anchor_id}_{seen[anchor_id]}"
        else:
            seen[anchor_id] = 1
        toc_items.append((level, text, anchor_id))
        # Insert id into the header tag
        old_tag = m.group(0)
        if 'id=' in old_tag:
            continue  # already has id
        new_tag = f'<h{level} id="{anchor_id}">{m.group(3)}</h{level}>' if m.group(2) is None else \
                  f'<h{level}{m.group(2)} id="{anchor_id}">{m.group(3)}</h{level}>'
        html_body = html_body.replace(old_tag, new_tag, 1)

    if not toc_items:
        return "", html_body

    # Build TOC HTML as a nested list
    toc_html = '<div id="toc">\n'
    toc_html += '<h2 id="toc-title">目录</h2>\n'
    prev_level = 0
    opened = [0]  # stack of whether we opened a list at each level
    for level, text, anchor_id in toc_items:
        if level > 3:
            continue
        # Close lists if going up
        while prev_level > level:
            toc_html += '</li>\n</ul>\n'
            prev_level -= 1
            opened[prev_level] = 0
        # Open new lists if going down
        while prev_level < level:
            toc_html += '<ul>\n'
            prev_level += 1
            if len(opened) <= prev_level:
                opened.append(1)
            else:
                opened[prev_level] = 1
        # Close previous item at same level
        if opened[prev_level]:
            toc_html += '</li>\n'
        # New item
        toc_html += f'<li><a href="#{anchor_id}">{html_mod.escape(text)}</a>'
        opened[prev_level] = 1

    # Close remaining open tags
    while prev_level > 1:
        toc_html += '</li>\n</ul>\n'
        prev_level -= 1
    if opened[prev_level]:
        toc_html += '</li>\n'
    if prev_level >= 1:
        toc_html += '</ul>\n'
    toc_html += '</div>\n'

    # Insert TOC before the first hr (--- separator), so cover page stays together
    first_hr = re.search(r'<hr\s*/?>', html_body)
    if first_hr:
        insert_pos = first_hr.start()
        html_body = html_body[:insert_pos] + '\n' + toc_html + '\n' + html_body[insert_pos:]

    return toc_html, html_body

toc_html, html_body = generate_toc(html_body)
print(f"  Generated TOC with {len(re.findall(r'<li>', toc_html))} entries")

# Add TOC CSS
TOC_CSS = """
#toc { page-break-before: always; page-break-after: always; margin-bottom: 20px; }
#toc-title { text-align: center; font-size: 16pt; color: #1a365d; border: none; margin-top: 30px; }
#toc ul { list-style: none; padding-left: 0; margin: 4px 0; }
#toc ul ul { padding-left: 20px; }
#toc li { margin: 3px 0; }
#toc a { text-decoration: none; color: #2b6cb0; font-size: 10pt; }
#toc a:hover { text-decoration: underline; }
"""

print("Step 4: Building styled HTML...")
CSS = TOC_CSS + """
@page {
    size: A4;
    margin: 1.6cm 1.8cm 2cm 1.8cm;
    @bottom-center {
        content: counter(page);
        font-family: "Microsoft YaHei", sans-serif;
        font-size: 8pt;
        color: #999;
    }
}
body {
    font-family: "Microsoft YaHei", "SimHei", "PingFang SC", sans-serif;
    font-size: 10pt;
    line-height: 1.7;
    color: #1a1a1a;
    text-align: left;
}
h1 {
    font-size: 16pt; color: #1a365d;
    border-bottom: 2px solid #3182ce; padding-bottom: 4px;
    margin-top: 26px;
}
h1:first-of-type { page-break-before: avoid; text-align: center; font-size: 20pt; border: none; margin-top: 60px; margin-bottom: 4px; }
/* 封面正文（版本、编制依据等）靠左对齐，标题除外 */
h1:first-of-type ~ p, h1:first-of-type ~ ul, h1:first-of-type ~ ol, h1:first-of-type ~ table { text-align: left; }
h2 { font-size: 13pt; color: #2a4365; border-bottom: 1px solid #cbd5e0; padding-bottom: 3px; margin-top: 20px; }
h3 { font-size: 11.5pt; color: #2d3748; margin-top: 16px; }
h4 { font-size: 10.5pt; color: #4a5568; margin-top: 12px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9pt; page-break-inside: avoid; }
th { background: #ebf4ff; color: #2b6cb0; font-weight: bold; padding: 4px 7px; border: 1px solid #cbd5e0; text-align: left; }
td { padding: 3px 7px; border: 1px solid #cbd5e0; vertical-align: top; }
tr:nth-child(even) { background: #f7fafc; }
code { font-family: Consolas, monospace; font-size: 8pt; background: #edf2f7; padding: 1px 3px; border-radius: 2px; }
pre code { display: block; padding: 6px 10px; background: #f7fafc; border: 1px solid #e2e8f0; font-size: 8pt; white-space: pre-wrap; }
img { max-width: 85%; height: auto; display: block; margin: 8px auto; }
div[align="center"] { text-align: center; margin: 8px 0; page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 14px 0; }
ul, ol { margin: 4px 0; padding-left: 20px; }
li { margin: 2px 0; }
strong { font-weight: 700; color: #2d3748; }
"""

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body>
</html>"""

html_file = WORK_DIR / "document.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Step 5: Generating PDF via Chrome headless...")
output_pdf = OUTPUT_DIR / "高岸ERP系统-需求说明书（V10.8，2026年5月8日）.pdf"
output_pdf_tmp = WORK_DIR / "output.pdf"

result = subprocess.run([
    CHROME,
    "--headless=new", "--disable-gpu",
    "--disable-web-security",
    "--allow-file-access-from-files",
    f"--print-to-pdf={output_pdf_tmp}",
    f"--print-to-pdf-no-header",
    f"file:///{html_file.as_posix()}"
], capture_output=True, timeout=120)

if output_pdf_tmp.exists():
    try:
        if output_pdf.exists():
            output_pdf.unlink()
        shutil.copy2(output_pdf_tmp, output_pdf)
        size = os.path.getsize(output_pdf)
        print(f"\nSUCCESS! PDF: {output_pdf}")
        print(f"Size: {size/1024:.0f} KB")
    except PermissionError:
        print(f"\nWARNING: {output_pdf.name} locked, temp file kept")
        size = os.path.getsize(output_pdf_tmp)
        print(f"Temp PDF size: {size/1024:.0f} KB")
        print(f"Temp path: {output_pdf_tmp}")
else:
    print(f"\nFAILED!")
    print(result.stderr.decode('utf-8', errors='replace')[:1000])

if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
print("Done.")
