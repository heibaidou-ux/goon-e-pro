"""Generate PDF from IoT simplified guide markdown with rendered SVG diagrams.

Strategy: MD -> HTML (with inline SVGs) -> Edge headless -> PDF

Changes from v1: inline SVG instead of base64 <img> for reliable PDF rendering.
"""
import re, subprocess, sys
from pathlib import Path

BASE = Path(r"C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP")
MD_FILE = BASE / "docs" / "02-设计" / "高岸ERP系统-盈隆店IoT接线实施指南（简版）（V1.0，2026年5月17日）.md"
OUTPUT = BASE / "docs" / "02-设计" / "高岸ERP系统-盈隆店IoT接线实施指南（简版）（V1.2，2026年5月18日）.pdf"
IMAGES = BASE / "docs" / "02-设计" / "images"
TMP_HTML = Path("C:/Users/王晓东/AppData/Local/Temp/iot_guide_v1.2.html")

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

md = MD_FILE.read_text(encoding="utf-8")

# Step 1: Replace SVG references with HTML-comment placeholders.
# Can NOT use text placeholders like ___SVG0___ because markdown_it
# interprets underscores as emphasis markers and mangles them.
placeholders = {}

def svg_to_placeholder(match):
    alt = match.group(1)
    path = match.group(2)
    svg_file = IMAGES / path
    if svg_file.exists():
        svg_content = svg_file.read_text(encoding="utf-8")
        idx = len(placeholders)
        placeholder = f"<!--IOT_SVG_{idx}-->"
        placeholders[placeholder] = svg_content
        return placeholder
    return match.group(0)

md = re.sub(r'!\[(.*?)\]\(images/(.*?\.svg)\)', svg_to_placeholder, md)

# Step 2: Convert MD to HTML
from markdown_it import MarkdownIt
md_parser = MarkdownIt('default', {'breaks': True, 'html': True})
html_body = md_parser.render(md)

# Step 3: Replace placeholders with inline SVGs
# Wrap SVG in a centered div with explicit size control for print
if placeholders:
    svg_styles = """
    svg.iot-diagram {
        max-width: 95%;
        height: auto;
        display: block;
        margin: 12px auto;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        background: #ffffff;
    }
    .iot-diagram-wrapper {
        text-align: center;
        margin: 15px 0;
        page-break-inside: avoid;
    }
"""
    for placeholder, svg_content in placeholders.items():
        # Ensure the SVG has the iot-diagram class for styling
        styled_svg = svg_content.replace("<svg", '<svg class="iot-diagram"')
        replacement = f'<div class="iot-diagram-wrapper">{styled_svg}</div>'
        html_body = html_body.replace(placeholder, replacement)
else:
    svg_styles = ""

# Step 4: Build complete HTML with print CSS
CSS = f"""
@page {{ size: A4; margin: 1.5cm 1.8cm 2cm 1.8cm; }}
body {{ font-family: "Microsoft YaHei","SimHei",sans-serif; font-size: 10pt; line-height: 1.7; color: #1a1a1a; }}
h1 {{ font-size: 16pt; color: #1a365d; border-bottom: 2px solid #3182ce; padding-bottom: 4px; margin-top: 26px; }}
h1:first-of-type {{ text-align: center; font-size: 20pt; border: none; margin-top: 40px; }}
h2 {{ font-size: 13pt; color: #2a4365; border-bottom: 1px solid #cbd5e0; padding-bottom: 3px; margin-top: 20px; }}
h3 {{ font-size: 11.5pt; color: #2d3748; margin-top: 16px; }}
table {{ width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9pt; }}
th {{ background: #ebf4ff; color: #2b6cb0; font-weight: bold; padding: 4px 7px; border: 1px solid #cbd5e0; text-align: left; }}
td {{ padding: 3px 7px; border: 1px solid #cbd5e0; vertical-align: top; }}
tr:nth-child(even) {{ background: #f7fafc; }}
code {{ font-family: Consolas, monospace; font-size: 8pt; background: #edf2f7; padding: 1px 3px; }}
pre code {{ display: block; padding: 6px 10px; background: #f7fafc; border: 1px solid #e2e8f0; white-space: pre-wrap; }}
hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 14px 0; }}
ul, ol {{ margin: 4px 0; padding-left: 20px; }}
li {{ margin: 2px 0; }}
blockquote {{ border-left: 3px solid #3182ce; padding: 8px 12px; margin: 8px 0; background: #f7fafc; font-size: 9.5pt; }}
{svg_styles}
@media print {{ svg.iot-diagram {{ max-width: 95%; }} table {{ font-size: 8pt; }} }}
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body>
</html>"""

TMP_HTML.write_text(encoding="utf-8", data=html)
print(f"HTML written: {TMP_HTML} ({len(html)} chars)")
print(f"SVGs embedded: {len(placeholders)} (inline)")

# Step 5: Find browser
browser = None
for b in BROWSERS:
    if Path(b).exists():
        browser = b
        break

if not browser:
    print("ERROR: No Edge/Chrome found. Open the HTML file manually and print to PDF.")
    print(f"HTML: file:///{TMP_HTML.as_posix()}")
    sys.exit(1)

print(f"Using browser: {browser}")

# Step 6: Run headless print-to-PDF
cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    f"--print-to-pdf={OUTPUT}",
    f"--print-to-pdf-no-header",
    f"file:///{TMP_HTML.as_posix()}",
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if OUTPUT.exists():
        print(f"PDF generated: {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")
        TMP_HTML.unlink(missing_ok=True)
    else:
        print("ERROR: PDF not created")
        print(f"STDERR: {result.stderr[:500] if result.stderr else 'none'}")
except Exception as e:
    print(f"ERROR: {e}")
    print(f"HTML debug file: file:///{TMP_HTML.as_posix()}")
    sys.exit(1)
