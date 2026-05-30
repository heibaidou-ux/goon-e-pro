"""Generate V1.1 drawio topology diagram for 盈隆店音频与485总线系统."""
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def tag(name, attrs=None, text=None):
    el = ET.Element(name)
    if attrs:
        for k, v in attrs.items():
            if v is not None:
                el.set(k, str(v))
    if text:
        el.text = text
    return el

def cell(_id, parent="1", style=None, vertex=None, edge=None, value="", geometry=None):
    attrs = {"id": str(_id), "parent": str(parent)}
    if style: attrs["style"] = style
    if vertex is not None: attrs["vertex"] = str(vertex)
    if edge is not None: attrs["edge"] = str(edge)
    if value: attrs["value"] = value
    el = tag("mxCell", attrs)
    if geometry:
        g = tag("mxGeometry", geometry)
        el.append(g)
    return el

def rect(_id, x, y, w, h, style, value="", parent="1"):
    return cell(_id, parent=parent, style=style, vertex="1", value=value,
                geometry={"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

def line(_id, x1, y1, x2, y2, style, parent="1"):
    return cell(_id, parent=parent, style=style, edge="1",
                geometry={"x": str(x1), "y": str(y1), "width": str(x2-x1), "height": str(y2-y1), "as": "geometry"})

# ── Build Page 1: Topology ──
p1 = tag("diagram", {"id": "topology", "name": "音频与485总线拓扑"})
model = tag("mxGraphModel", {"dx": "0", "dy": "0", "grid": "1", "gridSize": "10",
    "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
    "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "1600", "pageHeight": "1200",
    "math": "0", "shadow": "0"})
root = tag("root")
root.append(tag("mxCell", {"id": "0"}))
root.append(tag("mxCell", {"id": "1", "parent": "0"}))

cid = [100]

def nid():
    cid[0] += 1
    return cid[0]

# Title
root.append(rect(nid(), 30, 10, 1340, 35,
    "text;strokeColor=none;fillColor=none;align=center;fontSize=18;fontStyle=4",
    "<b>盈隆店智能音频与485总线系统接线拓扑图（V1.1 · 双功放架构）</b>"))

# Rack bounding box
root.append(rect(nid(), 20, 55, 1560, 200,
    "rounded=1;strokeColor=#566573;fillColor=#f5f5f5;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>工作间 · 19寸标准机柜（核心设备区）</b>"))

# Row 1: Side-mounted 485/power
root.append(rect(nid(), 40, 90, 240, 55,
    "rounded=1;strokeColor=#d35400;fillColor=#fdebd0;fontSize=10;html=1;",
    "<b>🔌 侧挂：明纬24V电源</b><br><font style=\"font-size:8px\">AC 220V → DC 24V/10A<br>为全店485设备供电</font>"))

root.append(rect(nid(), 310, 90, 240, 55,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=10;html=1;",
    "<b>🔗 侧挂：隔离USB转485</b><br><font style=\"font-size:8px\">HA控制主机 → 485总线<br>带隔离保护防串扰</font>"))

root.append(rect(nid(), 580, 90, 240, 55,
    "rounded=1;strokeColor=#1a5276;fillColor=#d5d8dc;fontSize=10;html=1;",
    "<b>📡 侧挂：8路隔离集线器</b><br><font style=\"font-size:8px\">星型拓扑 | 各房间CH1-CH6<br>信号再生 | 端口内置120Ω</font>"))

# Row 2: Front-mount audio equipment
root.append(rect(nid(), 850, 90, 220, 55,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=10;html=1;",
    "<b>🎤 无线话筒接收机（1U）</b><br><font style=\"font-size:8px\">一拖八 · 8天线 · 紧凑型<br>MIX OUT → 会议功放MIC 1</font>"))

root.append(rect(nid(), 1100, 90, 220, 55,
    "rounded=1;strokeColor=#1e8449;fillColor=#d5f5e3;fontSize=10;html=1;",
    "<b>🎵 会议独立数字功放（1U）</b><br><font style=\"font-size:8px\">移频防啸叫 · 双通道立体声<br>CH A→左2只  CH B→右2只</font>"))

root.append(rect(nid(), 1350, 90, 210, 55,
    "rounded=1;strokeColor=#1e8449;fillColor=#d5f5e3;fontSize=10;html=1;",
    "<b>🎵 4分区商用功放（2U）</b><br><font style=\"font-size:8px\">AUX1-4独立 · EMC优先广播<br>→ 4包间各1只音箱</font>"))

# Connections in rack
root.append(line(nid(), 1070, 117, 1100, 117,
    "strokeWidth=1;strokeColor=#1e8449;dashed=1;"))
# Label on the line
root.append(rect(nid(), 960, 78, 180, 18,
    "text;strokeColor=none;fillColor=none;fontSize=8;fontColor=#1e8449;align=center",
    "MIX OUT (6.35mm) → MIC 1"))

# Subtitle
root.append(rect(nid(), 40, 160, 1500, 25,
    "text;strokeColor=none;fillColor=none;align=left;fontSize=9;fontColor=#7f8c8d;",
    "<i>▼ 485总线：屏蔽网线（橙/橙白=V+ 绿/绿白=V- 蓝=485A 蓝白=485B 屏蔽层=单端接地）</i>"))

# Sidebar: Rack layout
root.append(rect(nid(), 40, 195, 180, 140,
    "text;strokeColor=#566573;fillColor=#f8f9fa;fontColor=#333;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;rounded=1;overflow=hidden",
    "<b>📐 机柜排布（上→下）</b><br><font style=\"font-size:8px\">① 话筒接收机（1U）<br>② 通风盲板（1U）<br>③ 会议独立功放（1U）<br>④ 4分区商用功放（2U）<br>⑤ 空U/理线（5U余量）<br><br><i>侧挂：</i><br>485集线器 | USB转485<br>24V电源 | 485控制模块</font>"))

# ── CH labels and room boxes ──
ch_data = [
    ("CH1", "Z1", "大会议室", "01", "左2只+右2只", "会议功放CH A+B"),
    ("CH2", "Z2", "中茶室A", "02", "1只", "4分区功放 AUX1"),
    ("CH3", "Z3", "中茶室B", "03", "1只", "4分区功放 AUX2"),
    ("CH4", "Z4", "大茶室C", "04", "1只", "4分区功放 AUX3"),
    ("CH5", "Z5", "走廊", "05", "1只", "4分区功放 AUX4"),
    ("CH6", "Z6", "展厅/前台", "06", "1只（待定音源）", "待定"),
]

col_x = [110, 340, 570, 800, 1030, 1260]
ch_y = 280
zone_y = 305
box_y = 360
box_w = 230
box_h = 180

for i, (ch, zn, room, sid, spk, amp) in enumerate(ch_data):
    x = col_x[i]
    root.append(rect(nid(), x, ch_y, 50, 20,
        "text;strokeColor=none;fillColor=#ebf5fb;fontSize=11;fontColor=#1a5276;align=center;rounded=1",
        f"<b>{ch}</b>"))
    root.append(rect(nid(), x, zone_y, 50, 20,
        "text;strokeColor=none;fillColor=#e8f8f5;fontSize=10;fontColor=#1e8449;align=center;rounded=1",
        f"<b>{zn}</b>"))

    # Room box
    box_content = (f"<b>{ch} · {room}</b>"
                   f"<br><font style=\"font-size:8px\">Slave ID={sid} | 吊顶电箱HT-8位</font>")
    root.append(rect(nid(), x-30, box_y, box_w, box_h,
        "rounded=1;strokeColor=#1a5276;fillColor=#eaf2f8;fontSize=11;fontStyle=1;html=1;verticalAlign=top;spacingTop=4",
        box_content))

    # Relay module inside
    root.append(rect(nid(), x-20, box_y+35, 100, 45,
        "rounded=1;strokeColor=#d35400;fillColor=#fef9e7;fontSize=9;html=1;",
        "<b>聚英8路继电器</b><br><font style=\"font-size:7px\">V+/V- 485A/B<br>DO×8</font>"))

    # Speaker
    root.append(rect(nid(), x+90, box_y+35, 100, 45,
        "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=9;html=1;",
        f"<b>{'🎵 ' + spk}</b><br><font style=\"font-size:7px\">Bose吸顶<br>100V/8W定压</font>"))

    # Audio driver text
    driver_color = "#1e8449" if "会议" in amp or "4分区" in amp else "#7f8c8d"
    root.append(rect(nid(), x-20, box_y+85, 210, 20,
        f"rounded=1;strokeColor={driver_color};fillColor=#f0faf1;fontSize=8;html=1;",
        f"<b>🔊 {amp}</b>"))

    # Loads
    loads = "照明×2 + 空调 + 窗帘"
    if room == "大会议室":
        loads = "照明×2 + 空调 + 窗帘"
    elif room == "走廊":
        loads = "照明×3"
    elif room == "展厅/前台":
        loads = "照明×2"
    else:
        loads = "照明×2 + 空调 + 窗帘 + 排风"

    root.append(rect(nid(), x-20, box_y+110, 210, 25,
        "rounded=1;strokeColor=#c0392b;fillColor=#fdedec;fontSize=9;html=1;",
        f"<b>⚡ 负载：</b>{loads}"))

    # EC: electric kettle for rooms that have it
    if room in ("中茶室A", "中茶室B", "大茶室C"):
        root.append(rect(nid(), x-20, box_y+140, 210, 25,
            "rounded=1;strokeColor=#bf360c;fillColor=#fbe9e7;fontSize=8;html=1;",
            "🔥 电茶炉1500W（经25A接触器）"))

    # Bluetooth wall panel indicator for 包间
    if room in ("中茶室A", "中茶室B", "大茶室C", "走廊"):
        root.append(rect(nid(), x-20, box_y+165, 210, 12,
            "rounded=1;strokeColor=#7f8c8d;fillColor=#d5d8dc;fontSize=7;html=1;",
            "🔵 86蓝牙墙插面板 → 网线音频回传 → 4分区功放"))

    # Arrow connector from rack to room
    root.append(line(nid(), x+50, 240, x+50, box_y,
        "strokeWidth=1;strokeColor=#1a5276;"))

# Legend
root.append(rect(nid(), 20, 600, 1560, 55,
    "text;strokeColor=#d35400;fillColor=#fbfcfc;fontSize=11;fontColor=#333;align=center;verticalAlign=middle;rounded=1;strokeWidth=2",
    "<b>网线线芯分配（每根屏蔽网线同时承载供电+信号）：</b><br>"
    "<font style=\"font-size:9px\">"
    "橙白+橙 = V+ (DC 24V)  |  绿白+绿 = V- (GND)  |  蓝 = 485A (D+)  |  "
    "蓝白 = 485B (D-)  |  棕/棕白 = 备用  |  屏蔽层 = 总柜端单端接地</font>"))

root.append(rect(nid(), 20, 670, 1560, 25,
    "text;strokeColor=none;fillColor=none;align=center;fontSize=9;fontColor=#7f8c8d",
    "图例：蓝色线=485总线信号  |  绿色线=音频信号（虚线）  |  橙色线=24V直流供电  |  红色线=220V强电"))

model.append(root)
p1.append(model)

# ── Build Page 2: Single Room Detail ──
p2 = tag("diagram", {"id": "room_detail", "name": "单房间接线详图"})
model2 = tag("mxGraphModel", {"dx": "0", "dy": "0", "grid": "1", "gridSize": "10",
    "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
    "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "1200", "pageHeight": "1000",
    "math": "0", "shadow": "0"})
root2 = tag("root")
root2.append(tag("mxCell", {"id": "0"}))
root2.append(tag("mxCell", {"id": "1", "parent": "0"}))

cid2 = [2000]

def nid2():
    cid2[0] += 1
    return cid2[0]

# Title
root2.append(rect(nid2(), 20, 10, 1160, 30,
    "text;strokeColor=none;fillColor=none;align=center;fontSize=16;fontStyle=4",
    "<b>单个房间接线详图（双功放架构 · 以包间为例）</b>"))

# Source from rack
root2.append(rect(nid2(), 20, 50, 1160, 85,
    "rounded=1;strokeColor=#566573;fillColor=#f5f5f5;fontSize=12;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>来自总弱电柜（工作间机柜）</b>"))

root2.append(rect(nid2(), 30, 80, 260, 40,
    "rounded=1;strokeColor=#1a5276;fillColor=#fbfcfc;fontSize=9;html=1;",
    "<b>屏蔽网线（SFTP）</b><br><font style=\"font-size:8px\">橙/橙白=V+  绿/绿白=V-  蓝=485A  蓝白=485B</font>"))

root2.append(rect(nid2(), 310, 80, 260, 40,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=9;html=1;",
    "<b>2×1.5mm² 音箱线</b><br><font style=\"font-size:8px\">无氧铜(OFC)阻燃双色护套线</font>"))

# Audio回传 line indicator
root2.append(rect(nid2(), 590, 80, 260, 40,
    "rounded=1;strokeColor=#7f8c8d;fillColor=#f4f6f6;fontSize=9;html=1;",
    "<b>CAT6网线（音频回传）</b><br><font style=\"font-size:8px\">86蓝牙面板 → 网线音频延长器 → 4分区功放AUX</font>"))

# Room ceiling box
root2.append(rect(nid2(), 20, 160, 1160, 260,
    "rounded=1;strokeColor=#1a5276;fillColor=#eaf2f8;fontSize=13;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>房间吊顶电箱（HT-8位/12位）</b>"))

# Relay module
root2.append(rect(nid2(), 30, 195, 300, 120,
    "rounded=1;strokeColor=#d35400;fillColor=#fef9e7;fontSize=10;html=1;fontColor=#333;",
    "<b><font style=\"font-size:11px\">聚英8路联动版继电器模块</font></b>"
    "<br><font style=\"font-size:8px\">"
    "┌─────────────────────────────┐<br>"
    "│ [V+]  [V-]  [485A] [485B]  │ ← 网线接入<br>"
    "│ [DI1] [DI2] [GND]          │ ← 预留<br>"
    "│                             │<br>"
    "│ COM1→NO1  COM2→NO2  ...    │ ← 强电输出<br>"
    "│ COM端子之间2.5mm²硬线跳线    │<br>"
    "└─────────────────────────────┘</font>"))

# Terminal blocks
root2.append(rect(nid2(), 360, 195, 180, 120,
    "rounded=1;strokeColor=#2c3e50;fillColor=#fbfcfc;fontSize=10;html=1;fontColor=#333;",
    "<b>接线端子排</b><br><font style=\"font-size:8px\">"
    "┌─────────────────────┐<br>"
    "│ 零线排 (N Bus)      │<br>"
    "├─────────────────────┤<br>"
    "│ 地线排 (PE Bus)     │<br>"
    "└─────────────────────┘</font>"))

# 485 panel
root2.append(rect(nid2(), 570, 195, 200, 70,
    "rounded=1;strokeColor=#7f8c8d;fillColor=#f4f6f6;fontSize=10;html=1;",
    "<b>🔘 485智能场景面板（三键六开）</b><br><font style=\"font-size:8px\">Modbus RTU从设备 | Slave ID 11-16<br>24V+485总线 | 预埋φ20弱电管</font>"))

# 86 Bluetooth panel (NEW)
root2.append(rect(nid2(), 800, 195, 200, 70,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=10;html=1;",
    "<b>🔵 86型蓝牙音频墙插面板</b><br><font style=\"font-size:8px\">蓝牙5.0接收 | 3.5mm/RCA线路输出<br>客人手机配对 → 音频回传机柜</font>"))

# 220V power
root2.append(rect(nid2(), 1020, 195, 140, 120,
    "rounded=1;strokeColor=#c0392b;fillColor=#fdedec;fontSize=10;html=1;",
    "<b>⚡ 220V市电进线</b><br><font style=\"font-size:8px\">从房间配电箱引来<br><br>"
    "<b>火线(L)</b> 2.5mm² → COM<br>"
    "<b>零线(N)</b> → 零线排<br>"
    "<b>地线(PE)</b> → 地线排</font>"))

# Section: Audio回传路径 (NEW)
root2.append(rect(nid2(), 20, 430, 1160, 80,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=11;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>🎵 音频回传路径（86蓝牙面板 → 4分区商用功放）</b>"))

root2.append(rect(nid2(), 30, 460, 1100, 40,
    "text;strokeColor=none;fillColor=none;fontSize=9;fontColor=#333;align=left;verticalAlign=middle",
    "【方案A】86蓝牙面板 3.5mm/RCA → 网线音频延长器发端（墙面86盒内）→ 预埋CAT6网线 → 机柜音频延长器收端 → RCA → 4分区功放 AUX n  "
    "  |  【方案B】86蓝牙面板 XLR平衡输出 → RVSP屏蔽线 → 机柜 → XLR转RCA → 4分区功放 AUX n"))

# Load output section
root2.append(rect(nid2(), 20, 530, 1160, 25,
    "text;strokeColor=none;fillColor=none;align=left;fontSize=12;fontStyle=1",
    "<b>▼ 负载输出分配</b>"))

loads = [
    ("CH1 · 照明", "灯具火线<br>线径: 1.5mm²", "#f39c12"),
    ("CH2 · 空调面板", "220V供电<br>线径: 1.5mm²", "#e74c3c"),
    ("CH3 · 电动窗帘", "电机电源<br>线径: 1.5mm²", "#9b59b6"),
    ("CH4 · 电茶炉", "→ 接触器线圈<br>线径: 2.5mm²", "#e74c3c"),
    ("CH5 · 辅助插座", "吧台/香薰<br>线径: 1.5mm²", "#2ecc71"),
    ("CH6 · 备用通道", "预留<br>线径: —", "#95a5a6"),
]
for i, (title, desc, color) in enumerate(loads):
    x = 30 + i * 190
    root2.append(rect(nid2(), x, 565, 175, 55,
        f"rounded=1;strokeColor={color};fillColor=#fdedec;fontSize=10;html=1;",
        f"<b>{title}</b><br><font style=\"font-size:8px\">{desc}</font>"))

# Special notes
root2.append(rect(nid2(), 30, 635, 540, 55,
    "rounded=1;strokeColor=#bf360c;fillColor=#fbe9e7;fontSize=10;html=1;",
    "<b>🔥 电茶炉交流接触器接线（强烈建议）</b><br>"
    "<font style=\"font-size:8px\">CH4(NO4) → 25A接触器线圈  |  接触器主触点(2.5mm²) → 电茶炉专用插座  |  "
    "避免1500W负载直接经过继电器模块端子</font>"))

root2.append(rect(nid2(), 590, 635, 570, 55,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=10;html=1;",
    "<b>🎵 吸顶音箱接线</b><br>"
    "<font style=\"font-size:8px\">安装前将参数旋钮拨至100V端 8W 或 16W（所有音箱保持一致）<br>"
    "红接红(+)，黑接黑(-)，确保同相位连接   |   多只并联时在接线端子上桥接</font>"))

# Warnings
root2.append(rect(nid2(), 20, 710, 1160, 55,
    "text;strokeColor=#c0392b;fillColor=#fdedec;fontSize=10;fontColor=#333;align=left;verticalAlign=middle;rounded=1;strokeWidth=2",
    "<b>⚠️ 施工特别提醒</b><br>"
    "<font style=\"font-size:9px;color:#c0392b;\">"
    "① 强弱电严禁共管：屏蔽网线必须单独走PVC弱电管，不能与220V强电线穿同一根管  |  "
    "② 24V正负极切勿接反：开机前务必用万用表测量网线末端确认极性，且与485A/B无短路  |  "
    "③ COM跳线必须使用2.5mm²铜芯硬线，端子螺丝完全拧死，特别是电茶炉回路  |  "
    "④ 86蓝牙面板供电确认：吊顶电箱取24V通过降压模块转5V供面板</font>"))

# Summary
root2.append(rect(nid2(), 20, 780, 1160, 40,
    "text;strokeColor=#1a5276;fillColor=#ebf5fb;fontSize=9;fontColor=#333;align=left;verticalAlign=middle;rounded=1",
    "<b>485总线参数：</b>Modbus RTU · 9600 bps · 总线长度≤100m · 隔离集线器端口内置120Ω（DIP启用）  |  "
    "<b>Slave ID：</b>继电器01-06 · 485面板11-16  |  "
    "<b>音频架构：</b>双功放（会议室立体声1U + 4分区商用2U） · 4路蓝牙墙插面板独立回传 · HA提示音经EMC插播"))

model2.append(root2)
p2.append(model2)

# ── Assemble and write ──
mxfile = tag("mxfile", {
    "host": "app.diagrams.net",
    "modified": "2026-05-16T15:00:00.000Z",
    "agent": "Python",
    "version": "24.2.5"
})
mxfile.append(p1)
mxfile.append(p2)

# Pretty-print
ET.indent(mxfile, space="  ")
xml_str = ET.tostring(mxfile, encoding="unicode", xml_declaration=True)

with open("高岸ERP系统-盈隆店智能音频与485总线接线示意图（V1.1）.drawio", "w", encoding="utf-8") as f:
    f.write(xml_str)

print("Draw.io V1.1 generated successfully!")
