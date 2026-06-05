"""
盈隆店 HA IoT — MQTT桥接（骨架）

后续联调流程：
1. M710Q 上部署 Mosquitto MQTT broker
2. 聚英继电器通过Modbus RTU → MQTT网关接入
3. 本桥接脚本将MQTT消息转为HA API调用

当前阶段：骨架代码，等待硬件联调
"""
import os, json, signal, sys
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.2.65")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_PREFIX = "yinglong/device/"

HA_URL = os.getenv("HA_URL", "http://192.168.2.65:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

running = True


def signal_handler(sig, frame):
    global running
    print("\n正在停止MQTT桥接...")
    running = False


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 50)
    print("盈隆店 MQTT 桥接服务")
    print("=" * 50)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"HA地址: {HA_URL}")
    print(f"主题前缀: {MQTT_TOPIC_PREFIX}")
    print()
    print("状态: 等待联调 — 部署Mosquitto后取消下方注释")
    print("=" * 50)

    # TODO: 部署MQTT后取消注释
    # import paho.mqtt.client as mqtt
    #
    # def on_connect(client, userdata, flags, rc):
    #     print(f"已连接MQTT Broker (rc={rc})")
    #     client.subscribe(f"{MQTT_TOPIC_PREFIX}+/command")
    #
    # def on_message(client, userdata, msg):
    #     topic = msg.topic
    #     payload = msg.payload.decode()
    #     print(f"收到消息: {topic} -> {payload}")
    #     # 解析并调用HA API
    #
    # client = mqtt.Client()
    # client.on_connect = on_connect
    # client.on_message = on_message
    # client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # client.loop_forever()

    # 当前：保持运行但不做任何事
    print("按 Ctrl+C 退出")
    while running:
        signal.pause()


if __name__ == "__main__":
    main()
