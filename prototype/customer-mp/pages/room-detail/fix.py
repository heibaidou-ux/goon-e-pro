import re

path = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\prototype\customer-mp\pages\room-detail\index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace renderPage's bookable innerHTML
old_line_2 = """  page.innerHTML =
    '<div class="room-header-card ' + gc + '"><div class="room-header-top"><div class="room-header-icon">' + (heroes[room.type]||'🏠') + '</div><div><div class="room-header-name">' + room.name + '</div><div class="room-header-meta">容纳 ' + room.capacity + '人 · ' + room.area + '㎡ · ¥' + hourRate + '/小时</div></div></div><div class="room-header-tags">' + facTags + '</div></div>' +
    '<div class="date-bar" id="dateBar"></div>' +
    '<div class="duration-section"><div class="section-label">选择时长</div><div class="duration-grid" id="durationGrid"></div></div>' +
    '<div id="timeArea" style="display:none"><div class="time-header"><span class="time-header-label" id="timeHeaderLabel">选择开始时间</span><button class="now-btn" onclick="pickNow()">⚡ 现在开始</button></div><div class="time-section"><div class="time-grid" id="timeGrid"></div><div style="font-size:10px;color:#999;margin-top:6px;display:flex;gap:12px"><span style="display:inline-flex;align-items:center;gap:3px"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#fff8e1;border:1px solid #ffe082"></span> 保洁准备中(15min)</span><span style="display:inline-flex;align-items:center;gap:3px"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#f5f5f5"></span> 已预约</span></div></div></div>' +
    '<div class="inpage-bottom"><div class="inpage-total"><span class="total-label">小计</span><span class="total-price" id="totalPrice">¥0</span><span class="total-detail" id="totalDetail">请选择时长和时间</span></div><button class="inpage-book-btn" id="bookBtn" disabled onclick="goPay()">确认预约</button></div>';"""

new_line_2 = """  page.innerHTML =
    '<div class="room-header-card ' + gc + '"><div class="room-header-top"><div class="room-header-icon">' + (heroes[room.type]||'🏠') + '</div><div><div class="room-header-name">' + room.name + '</div><div class="room-header-meta">容纳 ' + room.capacity + '人 · ' + room.area + '㎡ · ¥' + hourRate + '/小时</div></div></div><div class="room-header-tags">' + facTags + '</div></div>' +
    '<div class="date-bar" id="dateBar"></div>' +
    '<div class="duration-section"><div class="section-label">选择时长</div><div class="duration-grid" id="durationGrid"></div><div id="customDurationWrap" style="display:none;margin-top:6px"><select class="cd-select" id="customDurationSelect" onchange="pickCustomDuration(this.value)"><option value="">选择时长...</option></select></div></div>' +
    '<div id="timeRow" class="form-row" style="display:none"><div class="form-label">开始时间</div><button class="now-btn" id="nowBtn" onclick="pickNow()">⚡ 现在开始</button><span class="time-or">或</span><select id="timeSelect" onchange="pickTimeFromSelect(this.value)"><option value="">选择时间...</option></select></div>' +
    '<div class="info-bar"><span>🧹 保洁准备(15min)</span><span>📅 已预约自动屏蔽</span></div>' +
    '<div class="conflict-alert" id="conflictAlert"></div>' +
    '<div class="inpage-bottom"><div class="inpage-total"><span class="total-label">小计</span><span class="total-price" id="totalPrice">¥0</span><span class="total-detail" id="totalDetail">请选择时长和时间</span></div><button class="inpage-book-btn" id="bookBtn" disabled onclick="goPay()">确认预约</button></div>';"""

if old_line_2 in content:
    content = content.replace(old_line_2, new_line_2)
    print("Replaced renderPage OK")
else:
    print("renderPage NOT FOUND - checking exact bytes...")
    # Debug: find the partial pattern
    idx = content.find("timeArea")
    if idx >= 0:
        print(f"Found timeArea at {idx}")
        print(repr(content[idx-50:idx+50]))

# 2. Fix updateTotal -> updateBilling in renderPage
content = content.replace("  renderDateBar();\n  renderDurationGrid();\n  updateTotal();", "  renderDateBar();\n  renderDurationGrid();\n  updateBilling();")

# 3. Remove unused CSS (time-grid, time-cell, time-header, etc.)
old_css = """.time-header { display:flex; align-items:center; justify-content:space-between; padding:8px 12px 4px; }
.time-header-label { font-size:11px; color:#999; }
.now-btn { padding:6px 14px; border-radius:16px; background:#07c160; color:#fff; border:none; font-size:12px; font-weight:600; cursor:pointer; }
.now-btn:active { opacity:.8; }
.time-section { padding:4px 12px; }
.time-grid { display:flex; flex-wrap:wrap; gap:4px; overflow-y:auto; max-height:200px; border:1.5px solid #e5e5e5; padding:8px; }
.time-cell { padding:7px 2px; border-radius:6px; text-align:center; cursor:pointer; border:1px solid #eee; background:#fff; font-size:11px; transition:all .12s; width:calc(25% - 3px); flex-shrink:0; }
.time-cell:active { border-color:#07c160; }
.time-cell.selected { background:#07c160; color:#fff; border-color:#07c160; }
.time-cell .t-label { font-weight:500; }
.time-cell .t-price { font-size:9px; display:block; color:#999; }
.time-cell.selected .t-price { color:rgba(255,255,255,.7); }
.time-cell.disabled { cursor:not-allowed; }
.time-cell.disabled.booked { opacity:.35; background:#f5f5f5; border-color:#e0e0e0; }
.time-cell.disabled.cleaning { opacity:.7; background:#fff8e1; border-color:#ffe082; }

/* In-page bottom (subtotal + confirm) */"""

new_css = """/* In-page bottom (subtotal + confirm) */"""

content = content.replace(old_css, new_css)

# 4. Add missing new-row CSS if not already there (check if 'form-row' exists)
if 'form-row' not in content:
    # Add after the duration selector CSS
    old_break = '/* In-page bottom (subtotal + confirm) */'
    add_css = """
/* Form rows */
.form-row { padding:6px 12px; display:flex; align-items:center; gap:8px; }
.form-label { font-size:12px; font-weight:600; color:#333; min-width:48px; flex-shrink:0; }
.form-row .now-btn { padding:8px 16px; border-radius:16px; background:#07c160; color:#fff; border:none; font-size:12px; font-weight:600; cursor:pointer; white-space:nowrap; }
.form-row .now-btn:active { opacity:.8; }
.form-row .time-or { font-size:11px; color:#ccc; }
.form-row select { flex:1; padding:8px 10px; border-radius:8px; border:1.5px solid #e5e5e5; background:#fff; font-size:13px; color:#333; appearance:auto; }
.cd-select { padding:8px 12px; border-radius:8px; border:1.5px solid #07c160; background:#f0fdf4; font-size:13px; font-weight:600; color:#07c160; }
.conflict-alert { margin:4px 12px; padding:10px 14px; border-radius:8px; background:#fff3e0; border:1px solid #ffe082; font-size:12px; color:#e65100; display:none; }
.conflict-alert .suggest-time { color:#07c160; font-weight:600; cursor:pointer; text-decoration:underline; }
.info-bar { padding:2px 12px 6px; display:flex; gap:16px; font-size:10px; color:#999; }

/* In-page bottom (subtotal + confirm) */"""
    content = content.replace(old_break, add_css)

# 5. Remove unused getCellStatus function
old_gcs = """function getCellStatus(cMin, cEnd, roomId, dateStr) {
  var blocks = getBookedBlocks(roomId, dateStr);
  var nextDate = new Date(dateStr);
  nextDate.setDate(nextDate.getDate() + 1);
  var nextDateStr = nextDate.getFullYear() + '-' + String(nextDate.getMonth()+1).padStart(2,'0') + '-' + String(nextDate.getDate()).padStart(2,'0');
  var allBlocks = blocks.concat(getBookedBlocks(roomId, nextDateStr));
  for (var bi = 0; bi < allBlocks.length; bi++) {
    var b = allBlocks[bi];
    if (cMin < b.endMin && cEnd > b.startMin) return 'booked';
    if (cMin < b.endMin + 15 && cEnd > b.endMin) return 'cleaning';
  }
  return 'free';
}

"""

content = content.replace(old_gcs, "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
