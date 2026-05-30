"""Generate V1.2 drawio topology diagram for 盈隆店分布式网络IP音频+485总线系统."""
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
p1 = tag("diagram", {"id": "topology", "name": "网络与485总线拓扑"})
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
    "<b>盈隆店分布式网络IP音频与485总线系统拓扑图（V1.2 · 纯星型拓扑）</b>"))

# Rack bounding box
root.append(rect(nid(), 20, 55, 1560, 165,
    "rounded=1;strokeColor=#566573;fillColor=#f5f5f5;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>工作间 · 19寸标准机柜（10U）</b>"))

# Row 1: Front-mount equipment
root.append(rect(nid(), 40, 85, 210, 55,
    "rounded=1;strokeColor=#1a5276;fillColor=#d4e6f1;fontSize=10;html=1;",
    "<b>🔗 24口千兆网管交换机（1U）</b><br><font style=\"font-size:8px\">VLAN 10: 智能内网<br>VLAN 20: 客人外网</font>"))

root.append(rect(nid(), 290, 85, 210, 55,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d5d8dc;fontSize=10;html=1;",
    "<b>💾 QNAP NAS / HA主机（2U）</b><br><font style=\"font-size:8px\">双网口聚合<br>音频推流 + 485控制</font>"))

root.append(rect(nid(), 540, 85, 210, 55,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=10;html=1;",
    "<b>🎤 无线话筒接收机（1U）</b><br><font style=\"font-size:8px\">一拖八 · 8天线 · 紧凑型<br>MIX OUT → 会议室T-6715</font>"))

# Row 2: Side-mounted equipment
root.append(rect(nid(), 790, 85, 200, 55,
    "rounded=1;strokeColor=#d35400;fillColor=#fdebd0;fontSize=10;html=1;",
    "<b>🔌 侧挂：485串口服务器</b><br><font style=\"font-size:8px\">RJ45 → RS485<br>Modbus RTU over TCP</font>"))

root.append(rect(nid(), 1030, 85, 200, 55,
    "rounded=1;strokeColor=#1a5276;fillColor=#d5d8dc;fontSize=10;html=1;",
    "<b>📡 侧挂：8路隔离集线器</b><br><font style=\"font-size:8px\">星型拓扑 | CH1-CH6<br>信号再生 | 端口内置120Ω</font>"))

root.append(rect(nid(), 1270, 85, 200, 55,
    "rounded=1;strokeColor=#d35400;fillColor=#fdebd0;fontSize=10;html=1;",
    "<b>🔌 侧挂：明纬24V电源</b><br><font style=\"font-size:8px\">AC 220V → DC 24V/10A<br>为全店485设备供电</font>"))

# NAS→Switch connection
root.append(line(nid(), 500, 112, 250, 112,
    "strokeWidth=1;strokeColor=#1a5276;"))
root.append(rect(nid(), 300, 62, 180, 18,
    "text;strokeColor=none;fillColor=none;fontSize=8;fontColor=#1a5276;align=center",
    "双网口聚合"))

# Rack VLAN subtitle
root.append(rect(nid(), 40, 150, 1500, 22,
    "text;strokeColor=none;fillColor=none;align=left;fontSize=9;fontColor=#7f8c8d;",
    "<i>▼ 交换机VLAN：端口1-8 = VLAN 10（智能内网：T-6715×5 + NAS×1 + 串口服务器×1） | 端口9-20 = VLAN 20（客人外网：AP×5 + 有线网口×5 + 上联）</i>"))

# Sidebar: Rack layout
root.append(rect(nid(), 40, 180, 180, 115,
    "text;strokeColor=#566573;fillColor=#f8f9fa;fontColor=#333;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;rounded=1;overflow=hidden",
    "<b>📐 机柜排布（上→下）</b><br><font style=\"font-size:8px\">① 24口网管交换机（1U）<br>② 通风盲板（1U）<br>③ QNAP NAS/HA（2U）<br>④ 无线话筒接收机（1U）<br>⑤ 空U/理线（5U余量）<br><br><i>侧挂：</i><br>485串口服务器 | 485集线器<br>24V电源</font>"))

# ── Room data ──
ch_data = [
    ("CH1", "RM001", "大会议室", "01", "2只（立体声）", "itc T-6715"),
    ("CH2", "RM002", "中茶室A", "02", "1只（双音圈）", "itc T-6715"),
    ("CH3", "RM003", "中茶室B", "03", "1只（双音圈）", "itc T-6715"),
    ("CH4", "RM004", "大茶室C", "04", "1只（双音圈）", "itc T-6715"),
    ("CH5", "RM005", "走廊", "05", "1只", "itc T-6715"),
    ("CH6", "RM006", "展厅/前台", "06", "1只", "itc T-6715"),
]

col_x = [110, 340, 570, 800, 1030, 1260]
box_y = 330
box_w = 230
box_h = 230

for i, (ch, rm, room, sid, spk, audio) in enumerate(ch_data):
    x = col_x[i]

    # Room box
    box_content = (f"<b>{rm} · {room}</b>"
                   f"<br><font style=\"font-size:8px\">Slave ID={sid} | 吊顶电箱（加大号）</font>")
    root.append(rect(nid(), x-30, box_y, box_w, box_h,
        "rounded=1;strokeColor=#1a5276;fillColor=#eaf2f8;fontSize=11;fontStyle=1;html=1;verticalAlign=top;spacingTop=4",
        box_content))

    # T-6715 indicator (top area of room)
    root.append(rect(nid(), x-20, box_y+30, 210, 35,
        "rounded=1;strokeColor=#1e8449;fillColor=#d5f5e3;fontSize=9;html=1;",
        f"<b>🎵 itc T-6715 网络广播终端</b><br><font style=\"font-size:7px\">VLAN 10固定IP | LINE IN←蓝牙面板<br>SPK OUT→{spk}</font>"))

    # Relay module
    root.append(rect(nid(), x-20, box_y+70, 100, 40,
        "rounded=1;strokeColor=#d35400;fillColor=#fef9e7;fontSize=9;html=1;",
        "<b>聚英8路继电器</b><br><font style=\"font-size:7px\">DO×8</font>"))

    # Network indicators (3 lines)
    net_color = "#1e8449" if "itc" in audio else "#7f8c8d"
    root.append(rect(nid(), x+90, box_y+70, 100, 40,
        "rounded=1;strokeColor=#1a5276;fillColor=#ebf5fb;fontSize=7;html=1;",
        "<b>📶 3网线/房间</b><br><font style=\"font-size:6px\">① 设备网→T-6715<br>② AP面板<br>③ 有线网口</font>"))

    # Audio source
    root.append(rect(nid(), x-20, box_y+115, 210, 18,
        "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=8;html=1;",
        "<b>🔵 86蓝牙面板 → LINE IN（短距屏蔽线≤3米）</b>"))

    # Loads
    if room == "大会议室":
        loads = "照明×2 + 空调 + 窗帘"
    elif room == "走廊":
        loads = "照明×3"
    elif room == "展厅/前台":
        loads = "照明×2"
    else:
        loads = "照明×2 + 空调 + 窗帘 + 排风"

    root.append(rect(nid(), x-20, box_y+137, 210, 22,
        "rounded=1;strokeColor=#c0392b;fillColor=#fdedec;fontSize=8;html=1;",
        f"<b>⚡ 负载：</b>{loads}"))

    # EC: electric kettle
    if room in ("中茶室A", "中茶室B", "大茶室C"):
        root.append(rect(nid(), x-20, box_y+162, 210, 22,
            "rounded=1;strokeColor=#bf360c;fillColor=#fbe9e7;fontSize=7;html=1;",
            "🔥 电茶炉1500W（经25A接触器）"))

    # VLAN badge
    vlan_color = "#1e8449"
    root.append(rect(nid(), x-20, box_y+187, 210, 18,
        "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=7;html=1;",
        "<b>VLAN 10:</b> IP音频推流 + HTTP API  |  <b>VLAN 20:</b> AP/有线网"))

    # Arrow from rack
    root.append(line(nid(), x+50, 240, x+50, box_y,
        "strokeWidth=1;strokeColor=#1a5276;"))

# Legend
root.append(rect(nid(), 20, 600, 1560, 70,
    "text;strokeColor=#1a5276;fillColor=#fbfcfc;fontSize=10;fontColor=#333;align=left;verticalAlign=middle;rounded=1;strokeWidth=2;spacingLeft=12",
    "<b>每房间线缆汇总（5根 = 3网线 + 1 485 + 1音箱线）：</b><br>"
    "<font style=\"font-size:9px\">"
    "📶 网线①（设备网）：交换机VLAN 10 → 吊顶电箱T-6715 LAN IN（标准以太网T568B，纯数据不拆分）<br>"
    "📶 网线②（无线AP）：交换机VLAN 20 → 墙面86 AP面板（PoE可选）<br>"
    "📶 网线③（有线网）：交换机VLAN 20 → 桌边86网络墙插<br>"
    "🔌 485网线（24V+485）：485集线器CHn → 吊顶电箱继电器模块（色谱：橙/橙白=V+ 绿/绿白=V- 蓝=485A 蓝白=485B）<br>"
    "🔊 音箱线（2×1.5mm²）：T-6715 SPK OUT → Bose吸顶音箱</font>"))

root.append(rect(nid(), 20, 685, 1560, 25,
    "text;strokeColor=none;fillColor=none;align=center;fontSize=9;fontColor=#7f8c8d",
    "图例：绿色=VLAN 10智能内网  |  橙色=VLAN 20客人外网  |  蓝色=485总线  |  红色=220V强电  |  紫色=音频信号"))

model.append(root)
p1.append(model)

# ── Build Page 2: Single Room Detail ──
p2 = tag("diagram", {"id": "room_detail", "name": "单房间接线详图"})
model2 = tag("mxGraphModel", {"dx": "0", "dy": "0", "grid": "1", "gridSize": "10",
    "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
    "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "1200", "pageHeight": "1050",
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
    "<b>单个房间接线详图（V1.2 · 分布式网络IP音频架构 · 以包间为例）</b>"))

# Source: 3 network cables + 1 485 from rack
root2.append(rect(nid2(), 20, 50, 1160, 85,
    "rounded=1;strokeColor=#566573;fillColor=#f5f5f5;fontSize=12;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>来自总弱电柜（工作间机柜 · 4根线/房间）</b>"))

root2.append(rect(nid2(), 40, 80, 220, 40,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=9;html=1;",
    "<b>网线①（设备网）</b><br><font style=\"font-size:8px\">六类SFTP · VLAN 10<br>交换机→T-6715 LAN IN</font>"))

root2.append(rect(nid2(), 290, 80, 220, 40,
    "rounded=1;strokeColor=#f39c12;fillColor=#fef9e7;fontSize=9;html=1;",
    "<b>网线②（无线AP）</b><br><font style=\"font-size:8px\">六类SFTP · VLAN 20<br>交换机→86 AP面板</font>"))

root2.append(rect(nid2(), 540, 80, 220, 40,
    "rounded=1;strokeColor=#f39c12;fillColor=#fef9e7;fontSize=9;html=1;",
    "<b>网线③（有线网）</b><br><font style=\"font-size:8px\">六类SFTP · VLAN 20<br>交换机→桌边网口</font>"))

root2.append(rect(nid2(), 790, 80, 220, 40,
    "rounded=1;strokeColor=#1a5276;fillColor=#ebf5fb;fontSize=9;html=1;",
    "<b>485网线（24V+信号）</b><br><font style=\"font-size:8px\">屏蔽网线 · 485 HUB CHn<br>24V+485A/B</font>"))

root2.append(rect(nid2(), 1040, 80, 120, 40,
    "rounded=1;strokeColor=#95a5a6;fillColor=#f4f6f6;fontSize=8;html=1;fontColor=#7f8c8d;",
    "<b>📌 音箱线</b><br><font style=\"font-size:7px\">房间内本地布线<br>T-6715→吸顶音箱</font>"))

# Room ceiling box (larger to accommodate T-6715)
root2.append(rect(nid2(), 20, 160, 1160, 270,
    "rounded=1;strokeColor=#1a5276;fillColor=#eaf2f8;fontSize=13;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>房间吊顶电箱（加大号 ≥400×300mm）</b>"))

# T-6715 (NEW - replaces analog amp)
root2.append(rect(nid2(), 30, 195, 340, 110,
    "rounded=1;strokeColor=#1e8449;fillColor=#d5f5e3;fontSize=10;html=1;fontColor=#333;",
    "<b><font style=\"font-size:12px\">🎵 itc T-6715 网络广播功放终端</font></b>"
    "<br><font style=\"font-size:8px\">"
    "┌─────────────────────────────────────┐<br>"
    "│ [LAN IN] ← 网线①（VLAN 10固定IP）  │ ← HA音频推流 + HTTP API<br>"
    "│ [LINE IN] ← 86蓝牙面板（屏蔽音频线）│ ← 客人手机蓝牙音乐<br>"
    "│ [MIC IN]  ← 无线话筒MIX OUT（会议室）│ ← 话筒广播<br>"
    "│ [SPK OUT] L+L- R+R- 凤凰端子        │ → Bose吸顶音箱<br>"
    "│ [DC 24V]                           │ ← 吊顶电箱取电<br>"
    "└─────────────────────────────────────┘</font>"))

# Relay module
root2.append(rect(nid2(), 400, 195, 260, 110,
    "rounded=1;strokeColor=#d35400;fillColor=#fef9e7;fontSize=10;html=1;fontColor=#333;",
    "<b><font style=\"font-size:11px\">聚英8路联动版继电器模块</font></b>"
    "<br><font style=\"font-size:8px\">"
    "┌─────────────────────────────────────┐<br>"
    "│ [V+] [V-] [485A] [485B] ← 485网线  │<br>"
    "│ [DI1-DI8] [GND] ← 预留传感器       │<br>"
    "│ COM1→NO1  COM2→NO2  ...  COM8→NO8 │<br>"
    "│ COM端子之间2.5mm²硬线跳线           │<br>"
    "└─────────────────────────────────────┘</font>"))

# Terminal blocks
root2.append(rect(nid2(), 690, 195, 160, 110,
    "rounded=1;strokeColor=#2c3e50;fillColor=#fbfcfc;fontSize=10;html=1;fontColor=#333;",
    "<b>接线端子排</b><br><font style=\"font-size:8px\">"
    "┌────────────────────┐<br>"
    "│ 零线排 (N Bus)     │<br>"
    "├────────────────────┤<br>"
    "│ 地线排 (PE Bus)    │<br>"
    "└────────────────────┘</font>"))

# 220V power
root2.append(rect(nid2(), 880, 195, 130, 110,
    "rounded=1;strokeColor=#c0392b;fillColor=#fdedec;fontSize=10;html=1;",
    "<b>⚡ 220V进线</b><br><font style=\"font-size:8px\">从房间配电箱<br><br>"
    "<b>火线(L)</b> 2.5mm² → COM<br>"
    "<b>零线(N)</b> → 零线排<br>"
    "<b>地线(PE)</b> → 地线排</font>"))

# Wall devices section
root2.append(rect(nid2(), 20, 440, 1160, 90,
    "rounded=1;strokeColor=#566573;fillColor=#f5f5f5;fontSize=11;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>📶 墙面设备（86型面板）</b>"))

# 86 Bluetooth panel
root2.append(rect(nid2(), 30, 470, 230, 50,
    "rounded=1;strokeColor=#2c3e50;fillColor=#d4e6f1;fontSize=9;html=1;",
    "<b>🔵 86蓝牙音频墙插面板</b><br><font style=\"font-size:7px\">3.5mm/RCA → 金属屏蔽音频线（≤3米）<br>→ 吊顶电箱T-6715 LINE IN</font>"))

# 86 AP panel
root2.append(rect(nid2(), 290, 470, 230, 50,
    "rounded=1;strokeColor=#f39c12;fillColor=#fef9e7;fontSize=9;html=1;",
    "<b>📶 86无线AP面板（Wi-Fi 6）</b><br><font style=\"font-size:7px\">网线②（VLAN 20）<br>客人无线网络</font>"))

# 86 network wall jack
root2.append(rect(nid2(), 550, 470, 230, 50,
    "rounded=1;strokeColor=#f39c12;fillColor=#fef9e7;fontSize=9;html=1;",
    "<b>🔌 86有线网络墙插</b><br><font style=\"font-size:7px\">网线③（VLAN 20）<br>客人笔记本有线接入</font>"))

# 485 scene panel
root2.append(rect(nid2(), 810, 470, 230, 50,
    "rounded=1;strokeColor=#7f8c8d;fillColor=#d5d8dc;fontSize=9;html=1;",
    "<b>🔘 485智能场景面板（三键六开）</b><br><font style=\"font-size:7px\">Modbus RTU | Slave ID 11-16<br>吊顶电箱24V+485取电</font>"))

# Audio flow section
root2.append(rect(nid2(), 20, 540, 1160, 60,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=11;fontStyle=1;verticalAlign=top;spacingTop=4;spacingLeft=8",
    "<b>🎵 音频信号流（分布式IP架构）</b>"))

root2.append(rect(nid2(), 30, 565, 1140, 28,
    "text;strokeColor=none;fillColor=none;fontSize=8;fontColor=#333;align=left;verticalAlign=middle",
    "【IP推流】HA主机 → UDP/TCP → 24口交换机VLAN 10 → T-6715（固定IP）→ 内部解码 → SPK OUT → Bose吸顶音箱  |  "
    "【本地蓝牙】客人手机 → 86蓝牙面板 → 屏蔽音频线（≤3米）→ T-6715 LINE IN → 内部混合 → SPK OUT → Bose吸顶音箱  |  "
    "【话筒（会议室）】无线话筒接收机 MIX OUT → 6.35mm跳线 → T-6715 MIC IN"))

# 485 bus detail
root2.append(rect(nid2(), 20, 610, 1160, 25,
    "text;strokeColor=none;fillColor=none;align=left;fontSize=10;fontStyle=1",
    "<b>▼ 485总线接线（吊顶电箱内）</b>"))

root2.append(rect(nid2(), 30, 640, 1140, 35,
    "rounded=1;strokeColor=#1a5276;fillColor=#ebf5fb;fontSize=9;html=1;",
    "<b>485网线接入端子排：</b>"
    "橙+橙白=V+ → 继电器模块V+ 、485面板V+  |  "
    "绿+绿白=V- → 模块V- 、面板V-  |  "
    "蓝=485A → 模块485A 、面板485A  |  "
    "蓝白=485B → 模块485B 、面板485B  |  "
    "<b>屏蔽层：</b>总柜单端接地，吊顶端悬空"))

# Load output section
root2.append(rect(nid2(), 20, 685, 1160, 25,
    "text;strokeColor=none;fillColor=none;align=left;fontSize=10;fontStyle=1",
    "<b>▼ 负载输出分配（DO继电器）</b>"))

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
    root2.append(rect(nid2(), x, 720, 175, 50,
        f"rounded=1;strokeColor={color};fillColor=#fdedec;fontSize=10;html=1;",
        f"<b>{title}</b><br><font style=\"font-size:8px\">{desc}</font>"))

# Special notes
root2.append(rect(nid2(), 30, 785, 540, 50,
    "rounded=1;strokeColor=#bf360c;fillColor=#fbe9e7;fontSize=10;html=1;",
    "<b>🔥 电茶炉交流接触器接线（强烈建议）</b><br>"
    "<font style=\"font-size:8px\">CH4(NO4) → 25A接触器线圈  |  接触器主触点(2.5mm²) → 电茶炉专用插座  |  "
    "避免1500W负载直接经过继电器模块端子</font>"))

root2.append(rect(nid2(), 590, 785, 570, 50,
    "rounded=1;strokeColor=#1e8449;fillColor=#e8f8f5;fontSize=10;html=1;",
    "<b>🎵 Bose吸顶音箱档位</b><br>"
    "<font style=\"font-size:8px\">安装前统一拨至100V端 8W 或 16W（所有音箱保持一致）<br>"
    "立体声房间：L+/L-接左音箱，R+/R-接右音箱  |  单音箱房间：双音圈或T-6715设MONO模式</font>"))

# Warnings
root2.append(rect(nid2(), 20, 850, 1160, 50,
    "text;strokeColor=#c0392b;fillColor=#fdedec;fontSize=10;fontColor=#333;align=left;verticalAlign=middle;rounded=1;strokeWidth=2",
    "<b>⚠️ 施工特别提醒</b><br>"
    "<font style=\"font-size:9px;color:#c0392b;\">"
    "① 强弱电严禁共管：弱电线必须单独走PVC弱电管，不能与220V强电线穿同一根管  |  "
    "② T-6715需设VLAN 10固定IP，交换机端口绑定MAC  |  "
    "③ 485网线24V正负极切勿接反，开机前万用表测量确认  |  "
    "④ 吊顶电箱内强弱电分区：左侧T-6715+继电器+485，右侧220V进线+零地线排，间距≥10cm  |  "
    "⑤ 单音箱房间严禁物理短接L+和R+，T-6715后台设MONO模式或使用双音圈音箱</font>"))

# Summary
root2.append(rect(nid2(), 20, 915, 1160, 40,
    "text;strokeColor=#1a5276;fillColor=#ebf5fb;fontSize=9;fontColor=#333;align=left;verticalAlign=middle;rounded=1",
    "<b>VLAN：</b>VLAN 10=智能内网（T-6715×5 + NAS + 串口服务器） · VLAN 20=客人外网（AP×5 + 有线网口×5）  |  "
    "<b>485参数：</b>Modbus RTU · 9600 bps · 隔离集线器端口内置120Ω  |  "
    "<b>Slave ID：</b>继电器01-06 · 面板11-16  |  "
    "<b>音频架构：</b>分布式IP · 5× itc T-6715 · HA UDP/TCP推流 · 蓝牙面板本地LINE IN"))

model2.append(root2)
p2.append(model2)

# ── Assemble and write ──
mxfile = tag("mxfile", {
    "host": "app.diagrams.net",
    "modified": "2026-05-16T16:00:00.000Z",
    "agent": "Python",
    "version": "24.2.5"
})
mxfile.append(p1)
mxfile.append(p2)

ET.indent(mxfile, space="  ")
xml_str = ET.tostring(mxfile, encoding="unicode", xml_declaration=True)

with open("高岸ERP系统-盈隆店智能音频与485总线接线示意图（V1.2）.drawio", "w", encoding="utf-8") as f:
    f.write(xml_str)

print("Draw.io V1.2 generated successfully!")
