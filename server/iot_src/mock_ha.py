"""
盈隆店 HA IoT — 模拟HA服务器（本机测试用）
启动后在本机模拟 HA REST API，供 scripts/ 下的脚本测试
"""
import json, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "0.0.0.0"
PORT = 8123

PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>盈隆店 IoT 模拟面板</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'Microsoft YaHei',sans-serif;background:#f0f2f5;color:#333;padding:20px}
h1{font-size:22px;margin-bottom:8px;display:flex;align-items:center;gap:10px}
h1 small{font-size:13px;color:#999;font-weight:normal}
#status{font-size:13px;color:#666;margin-bottom:16px}
.rooms{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.room{background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.room h2{font-size:16px;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #e8ecf1}
.entity{display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f5f5f5}
.entity:last-child{border-bottom:none}
.entity .name{font-size:14px}
.btn{background:#1677ff;color:#fff;border:none;border-radius:6px;padding:4px 12px;cursor:pointer;font-size:13px}
.btn-on{background:#ff4d4f}
.btn:hover{opacity:.85}
.sensor-val{font-size:13px;color:#1677ff;font-weight:bold}
.tip{font-size:12px;color:#999;margin-top:12px;text-align:center}
.loading{color:#999;text-align:center;padding:40px 0}
.error{color:#ff4d4f;text-align:center;padding:40px 0}
</style>
</head>
<body>
<h1>盈隆店 IoT 设备面板 <small>模拟环境</small></h1>
<div id="status">加载中...</div>
<div class="rooms" id="rooms"><div class="loading">连接中...</div></div>
<div class="tip">点击按钮切换开关状态 | 页面每3秒自动刷新</div>
<script>
const ROOM_MAP = [
  ['大茶室',['大茶室按键1','大茶室按键2','大茶室按键3','大茶室按键4','大茶室按键5','大茶室按键6','大茶室总开关','大茶室筒灯','大茶室背景灯','大茶室吊灯','大茶室功放音量','大茶室窗帘','大茶室功放状态']],
  ['大会议室',['大会议室总开关','大会议室筒灯1','大会议室筒灯2','大会议室吊灯']],
  ['中茶室',['中茶室总开关','中茶室筒灯','中茶室吊灯','中茶室背景灯']],
  ['小茶室',['小茶室总开关','小茶室筒灯','小茶室排风扇']]
];
let entityMap = {};

async function load(){
  try {
    const r = await fetch('/api/states');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const list = await r.json();
    entityMap = {};
    list.forEach(function(e){ entityMap[e.entity_id] = e; });
    document.getElementById('status').textContent = '共 ' + list.length + ' 个实体 | 更新时间: ' + new Date().toLocaleTimeString();
    var html = '';
    for (var i = 0; i < ROOM_MAP.length; i++) {
      var room = ROOM_MAP[i];
      html += '<div class="room"><h2>' + room[0] + '</h2>';
      var names = room[1];
      for (var j = 0; j < names.length; j++) {
        var n = names[j];
        var e = entityMap['input_boolean.' + n] || entityMap['input_number.' + n] || entityMap['sensor.' + n];
        if (!e) continue;
        var parts = e.entity_id.split('.');
        var dom = parts[0];
        if (dom === 'sensor' || dom === 'input_number') {
          var val = e.state + (e.attributes.unit_of_measurement || '');
          html += '<div class="entity"><span class="name">' + e.attributes.friendly_name + '</span><span class="sensor-val">' + val + '</span></div>';
        } else {
          var isOn = e.state === 'on';
          html += '<div class="entity"><span class="name">' + e.attributes.friendly_name + '</span><button class="btn' + (isOn ? ' btn-on' : '') + '" data-eid="' + e.entity_id + '">' + (isOn ? '关闭' : '打开') + '</button></div>';
        }
      }
      html += '</div>';
    }
    document.getElementById('rooms').innerHTML = html;
  } catch (err) {
    document.getElementById('status').textContent = '加载失败: ' + err.message;
    document.getElementById('status').style.color = '#ff4d4f';
  }
}

document.getElementById('rooms').addEventListener('click', async function(ev){
  var btn = ev.target;
  if (btn.tagName !== 'BUTTON') return;
  var eid = btn.getAttribute('data-eid');
  if (!eid) return;
  var e = entityMap[eid];
  if (!e) return;
  var cur = e.state;
  var target = cur === 'on' ? 'off' : 'on';
  var svc = 'turn_' + (target === 'on' ? 'on' : 'off');
  try {
    await fetch('/api/services/input_boolean/' + svc, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({entity_id: eid})
    });
    load();
  } catch (err) {
    console.error(err);
  }
});

load();
setInterval(load, 3000);
</script>
</body>
</html>"""

# ── 模拟实体状态 ──
ENTITIES = {}

def make_entity(eid, state, name, **extra):
    return {
        "entity_id": eid,
        "state": state,
        "attributes": {"friendly_name": name, "icon": extra.get("icon", "mdi:lightbulb"), **extra},
        "last_changed": "2026-05-30T00:00:00+08:00",
        "last_updated": "2026-05-30T00:00:00+08:00",
        "context": {"id": str(uuid.uuid4()), "parent_id": None, "user_id": None},
    }

# 大茶室
ENTITIES["input_boolean.大茶室按键1"] = make_entity("input_boolean.大茶室按键1", "off", "大茶室按键1", icon="mdi:button")
ENTITIES["input_boolean.大茶室按键2"] = make_entity("input_boolean.大茶室按键2", "off", "大茶室按键2", icon="mdi:button")
ENTITIES["input_boolean.大茶室按键3"] = make_entity("input_boolean.大茶室按键3", "off", "大茶室按键3", icon="mdi:button")
ENTITIES["input_boolean.大茶室按键4"] = make_entity("input_boolean.大茶室按键4", "off", "大茶室按键4", icon="mdi:button")
ENTITIES["input_boolean.大茶室按键5"] = make_entity("input_boolean.大茶室按键5", "off", "大茶室按键5", icon="mdi:button")
ENTITIES["input_boolean.大茶室按键6"] = make_entity("input_boolean.大茶室按键6", "off", "大茶室按键6", icon="mdi:button")
ENTITIES["input_boolean.大茶室总开关"] = make_entity("input_boolean.大茶室总开关", "off", "大茶室总开关")
ENTITIES["input_boolean.大茶室筒灯"] = make_entity("input_boolean.大茶室筒灯", "off", "大茶室筒灯")
ENTITIES["input_boolean.大茶室背景灯"] = make_entity("input_boolean.大茶室背景灯", "off", "大茶室背景灯")
ENTITIES["input_boolean.大茶室吊灯"] = make_entity("input_boolean.大茶室吊灯", "off", "大茶室吊灯")
ENTITIES["input_number.大茶室功放音量"] = make_entity("input_number.大茶室功放音量", "50", "大茶室功放音量", min=0, max=100, step=1, unit_of_measurement="%")
ENTITIES["sensor.大茶室窗帘"] = make_entity("sensor.大茶室窗帘", "已打开", "大茶室窗帘", icon="mdi:curtains")
ENTITIES["sensor.大茶室功放状态"] = make_entity("sensor.大茶室功放状态", "在线", "大茶室功放状态", icon="mdi:speaker")

# 大会议室
ENTITIES["input_boolean.大会议室总开关"] = make_entity("input_boolean.大会议室总开关", "off", "大会议室总开关")
ENTITIES["input_boolean.大会议室筒灯1"] = make_entity("input_boolean.大会议室筒灯1", "off", "大会议室筒灯1")
ENTITIES["input_boolean.大会议室筒灯2"] = make_entity("input_boolean.大会议室筒灯2", "off", "大会议室筒灯2")
ENTITIES["input_boolean.大会议室吊灯"] = make_entity("input_boolean.大会议室吊灯", "off", "大会议室吊灯")

# 中茶室
ENTITIES["input_boolean.中茶室总开关"] = make_entity("input_boolean.中茶室总开关", "off", "中茶室总开关")
ENTITIES["input_boolean.中茶室筒灯"] = make_entity("input_boolean.中茶室筒灯", "off", "中茶室筒灯")
ENTITIES["input_boolean.中茶室吊灯"] = make_entity("input_boolean.中茶室吊灯", "off", "中茶室吊灯")
ENTITIES["input_boolean.中茶室背景灯"] = make_entity("input_boolean.中茶室背景灯", "off", "中茶室背景灯")

# 小茶室
ENTITIES["input_boolean.小茶室总开关"] = make_entity("input_boolean.小茶室总开关", "off", "小茶室总开关")
ENTITIES["input_boolean.小茶室筒灯"] = make_entity("input_boolean.小茶室筒灯", "off", "小茶室筒灯")
ENTITIES["input_boolean.小茶室排风扇"] = make_entity("input_boolean.小茶室排风扇", "off", "小茶室排风扇")


class MockHAHandler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    def _html(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            self._html(PAGE_HTML)
        elif self.path == "/api/states":
            self._json(list(ENTITIES.values()))
        elif self.path.startswith("/api/states/"):
            eid = self.path[len("/api/states/"):]
            if eid in ENTITIES:
                self._json(ENTITIES[eid])
            else:
                self._json({"error": "Entity not found"}, 404)
        elif self.path == "/api/config":
            self._json({"state": "RUNNING", "version": "mock-1.0", "location_name": "盈隆店（模拟）"})
        else:
            self._json({"error": "Not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path.startswith("/api/services/input_boolean/"):
            service = self.path.split("/")[-1]
            eid = body.get("entity_id", "")
            if eid and eid in ENTITIES:
                target = {"on": "on", "turn_on": "on", "off": "off", "turn_off": "off", "toggle": None}[service]
                if target:
                    ENTITIES[eid]["state"] = target
                else:
                    ENTITIES[eid]["state"] = "off" if ENTITIES[eid]["state"] == "on" else "on"
                print(f"  {eid} → {ENTITIES[eid]['state']}")
                self._json([ENTITIES[eid]])
            else:
                self._json({"error": "Entity not found"}, 404)

        elif self.path.startswith("/api/services/input_number/"):
            service = self.path.split("/")[-1]
            eid = body.get("entity_id", "")
            value = body.get("value")
            if eid and eid in ENTITIES and value is not None:
                ENTITIES[eid]["state"] = str(value)
                print(f"  {eid} → {value}")
                self._json([ENTITIES[eid]])
            else:
                self._json({"error": "Invalid request"}, 400)
        else:
            self._json({"error": "Not found"}, 404)

    def log_message(self, fmt, *args):
        print(f"[HA模拟] {args[0]} {args[1]}")


def main():
    server = HTTPServer((HOST, PORT), MockHAHandler)
    print(f"盈隆店 HA 模拟服务器")
    print(f"地址: http://{HOST}:{PORT}")
    print(f"API:  GET  /api/states")
    print(f"      POST /api/services/input_boolean/turn_on")
    print(f"      POST /api/services/input_boolean/turn_off")
    print(f"      POST /api/services/input_boolean/toggle")
    print(f"")
    print(f"共 {len(ENTITIES)} 个模拟实体")
    print(f"按 Ctrl+C 停止")
    print(f"{'='*50}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()


if __name__ == "__main__":
    main()
